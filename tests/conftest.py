"""Фикстуры интеграционных тестов: автоматический подъем и остановка локального стека.

Тесты пакета tests выполняются против полного docker-стека (приложение, PostgreSQL,
nginx, MinIO). Фикстура повторяет шаги задачи task test-integration, поэтому тесты
можно запускать напрямую через pytest без предварительной подготовки окружения.
"""

import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Корень репозитория: рабочий каталог команд Compose и поиска сертификата nginx.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Сервисы стека для интеграционных тестов: приложение с PostgreSQL обслуживают
# страницы, nginx терминирует HTTPS, MinIO хранит медиа.
STACK_SERVICES = ("application", "postgres", "nginx", "minio")

# Профили сервисов стека: без активных профилей down не видит профильные сервисы
# и оставляет их работать, если .env ограничивает набор профилей (например, postgres).
STACK_PROFILES = "postgres,minio,nginx"


def _compose_command_and_wait() -> tuple[list[str], tuple[str, ...]]:
    """Определить команду Compose и флаг ожидания готовности сервисов.

    Docker Compose V2 вызывается как "docker compose" и поддерживает --wait;
    для V1 ("docker-compose") ожидание healthcheck недоступно.

    Returns:
        Команда Compose и кортеж дополнительных флагов запуска
    """
    compose_v2 = (
        subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )
    return (["docker", "compose"], ("--wait",)) if compose_v2 else (["docker-compose"], ())


def _ensure_nginx_certificate() -> None:
    """Выпустить self-signed сертификат nginx, если он еще не выпущен.

    До первого выпуска сертификата nginx не стартует; выпуск повторяет задачу
    task dev-cert и выполняется той же командой.
    """
    domain = os.getenv("DOMAIN_NAME", default="localhost")
    certificate = PROJECT_ROOT / "nginx" / "letsencrypt" / "live" / domain / "fullchain.pem"
    if certificate.exists():
        return
    try:
        subprocess.run(["task", "dev-cert"], cwd=PROJECT_ROOT, check=True)
    except FileNotFoundError as error:
        message = (
            "Сертификат nginx не найден и утилита task недоступна: выпустите сертификат командой task dev-cert вручную"
        )
        raise RuntimeError(message) from error


@pytest.fixture(scope="session", autouse=True)
def integration_stack() -> Iterator[None]:
    """Поднять локальный стек перед сессией тестов и остановить после нее.

    Сессия начинается с полной остановки стека: остатки прошлой сессии
    (например, незавершенный прогон) помешали бы ожиданию healthcheck.
    Переменные окружения повторяют секцию env задачи test-integration:
    они задаются процессу Compose и имеют приоритет над значениями .env,
    а адреса сервисов нужны и самим тестам, читающим их из окружения.
    """
    load_dotenv()
    compose, wait_flags = _compose_command_and_wait()
    _ensure_nginx_certificate()

    os.environ.update(
        POSTGRES_HOST="postgres",
        DOMAIN_NAME=os.getenv("DOMAIN_NAME", default="localhost"),
        MINIO_SERVER_URL="http://127.0.0.1:9000",
        MINIO_BROWSER_REDIRECT_URL="http://127.0.0.1:9001",
    )

    def run_compose(action: list[str], profiles: str | None = None, *, check: bool = False) -> None:
        """Выполнить команду Compose от корня репозитория.

        Сбой остановки стека (down) не прерывает сессию: это техническая
        очистка, ее ошибки не влияют на результат тестов и видны в выводе.
        Сбой запуска (up) прерывает сессию - без стека тесты невыполнимы.

        Args:
            action: Аргументы команды Compose
            profiles: Активные профили; без значения профили не переопределяются
            check: Прервать сессию при ненулевом коде возврата команды
        """
        env = os.environ.copy()
        if profiles is not None:
            env["COMPOSE_PROFILES"] = profiles
        subprocess.run([*compose, *action], cwd=PROJECT_ROOT, env=env, check=check)

    run_compose(["down"], profiles=STACK_PROFILES)
    run_compose(["up", "-d", *wait_flags, *STACK_SERVICES], check=True)
    yield
    run_compose(["down"], profiles=STACK_PROFILES)
