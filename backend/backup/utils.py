"""Вспомогательные функции системы резервного копирования.

Вычисления и подготовка данных без выполнения операций: разбор списка
целей, именование дампов, выбор последнего дампа, сбор переменных libpq,
адресация медиа-хранилища для rclone и проверка обязательных параметров.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import CommandError

DUMP_FLAGS = ["-Fc", "--no-privileges", "--no-subscriptions", "--no-publications"]
DEFAULT_RETENTION_DAYS = 14
RETENTION_SLACK_DAYS = 1
SECONDS_PER_DAY = 86400
BYTES_PER_KIB = 1024
RCLONE_MEDIA_REMOTE = "media"  # имя remote; в переменных RCLONE_CONFIG_* пишется заглавными
MEDIA_S3_VARS = (  # обязательны для операций с медиа при STORAGE_TYPE=s3
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_S3_ENDPOINT_URL",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
)


def media_rclone_address() -> str:
    """Адрес медиа-хранилища для rclone.

    Returns:
        str: "media:бакет/префикс" при STORAGE_TYPE=s3 (remote собирается
        из RCLONE_CONFIG_* в media_rclone_env), иначе путь MEDIA_ROOT.

    Example:
        >>> media_rclone_address()
        'media:media-bucket/media'
    """
    if is_s3():
        return f"{RCLONE_MEDIA_REMOTE}:{settings.AWS_STORAGE_BUCKET_NAME}/{settings.S3_MEDIA_LOCATION}"
    return str(settings.MEDIA_ROOT)


def media_rclone_env() -> dict[str, str] | None:
    """Переменные RCLONE_CONFIG_* для rclone-доступа к медиа-бакету.

    ACL public-read выравнивает восстановление (pull_media) с загрузкой
    через сайт: приложение публикует медиа с этим ACL, а rclone сам по
    себе объектов публичными не делает.

    Returns:
        dict[str, str] | None: Переменные remote media при STORAGE_TYPE=s3,
        None при filesystem (rclone работает с локальным путем без настроек).

    Example:
        При STORAGE_TYPE=s3 и remote media возвращает, помимо прочего:
        >>> media_rclone_env()["RCLONE_CONFIG_MEDIA_TYPE"]
        's3'
    """
    if not is_s3():
        return None
    remote = RCLONE_MEDIA_REMOTE.upper()
    return {
        f"RCLONE_CONFIG_{remote}_TYPE": "s3",
        f"RCLONE_CONFIG_{remote}_PROVIDER": "Other",
        f"RCLONE_CONFIG_{remote}_ENDPOINT": settings.AWS_S3_ENDPOINT_URL,
        f"RCLONE_CONFIG_{remote}_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
        f"RCLONE_CONFIG_{remote}_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
        f"RCLONE_CONFIG_{remote}_REGION": settings.AWS_S3_REGION_NAME,
        f"RCLONE_CONFIG_{remote}_ACL": "public-read",
    }


def load_target_list(targets_value: str | None) -> list[str]:
    """Разбить строку адресов целей на список.

    Args:
        targets_value (str | None): Значение настроек BACKUP_TARGETS.

    Returns:
        list[str]: Адреса целей; пустая строка или None дают пустой список.

    Example:
        >>> load_target_list("/mnt/backup yadisk:site-backup")
        ['/mnt/backup', 'yadisk:site-backup']
    """
    return targets_value.split() if targets_value else []


def now_local() -> datetime:
    """Текущее время в таймзоне проекта (settings.TIME_ZONE, Europe/Moscow)."""
    return datetime.now(ZoneInfo(settings.TIME_ZONE))


def dump_filename(db_name: str) -> str:
    """Имя дампа: <база>_<дата>_<время>.dump в МСК (Europe/Moscow).

    Дата и время в имени обеспечивают лексикографическую сортировку
    от старых к новым, на которую опирается latest_dump.

    Args:
        db_name (str): Имя базы данных.

    Returns:
        str: Имя файла дампа.

    Example:
        >>> dump_filename("personal_website")
        'personal_website_2026-08-25_1657.dump'
    """
    stamp = now_local().strftime("%Y-%m-%d_%H%M")
    return f"{db_name}_{stamp}.dump"


def latest_dump(names: list[str]) -> str:
    """Последний дамп по имени (имена датированы и сортируются лексикографически).

    Args:
        names (list[str]): Имена дампов цели.

    Returns:
        str: Имя самого свежего дампа.

    Raises:
        CommandError: Список пуст.

    Example:
        >>> latest_dump(["db_2026-08-20_1200.dump", "db_2026-08-21_0800.dump"])
        'db_2026-08-21_0800.dump'
    """
    if not names:
        msg = "список дампов пуст"
        raise CommandError(msg)
    return sorted(names)[-1]


def pg_env() -> dict[str, str]:
    """Собрать переменные libpq (PG*) из настроек подключения к БД.

    pg_dump/pg_restore не читают POSTGRES_* приложения, а используют
    переменные libpq PG*; значения берутся из settings.DATABASES.

    Returns:
        dict[str, str]: Переменные PGHOST, PGPORT, PGDATABASE, PGUSER,
        PGPASSWORD; при sslmode/sslrootcert в OPTIONS - также PGSSLMODE
        и PGSSLROOTCERT.

    Example:
        >>> pg_env()["PGDATABASE"]
        'personal_website'
    """
    cfg = settings.DATABASES["default"]
    pg = {
        "PGHOST": str(cfg["HOST"]),
        "PGPORT": str(cfg["PORT"]),
        "PGDATABASE": str(cfg["NAME"]),
        "PGUSER": str(cfg["USER"]),
        "PGPASSWORD": str(cfg["PASSWORD"]),
    }
    opts = cfg.get("OPTIONS") or {}
    if opts.get("sslmode"):
        pg["PGSSLMODE"] = str(opts["sslmode"])
    if opts.get("sslrootcert"):
        pg["PGSSLROOTCERT"] = str(opts["sslrootcert"])
    return pg


def storage_type() -> str:
    """Текущий тип хранилища (filesystem по умолчанию)."""
    return settings.STORAGE_TYPE


def is_s3() -> bool:
    """Хранилище - S3."""
    return storage_type() == "s3"


def require_pg_env() -> None:
    """Проверить наличие обязательных параметров подключения к БД.

    Raises:
        CommandError: В settings.DATABASES не задан один из параметров
            HOST, PORT, NAME, USER, PASSWORD.
    """
    cfg = settings.DATABASES["default"]
    required = ["HOST", "PORT", "NAME", "USER", "PASSWORD"]
    missing = [name for name in required if not cfg.get(name)]
    if missing:
        msg = f"параметр подключения {', '.join(missing)} не задан в настройках базы данных"
        raise CommandError(msg)


def require_media_env() -> None:
    """Проверить настройки S3, обязательные для операций с медиа при s3.

    При filesystem обязательные настройки отсутствуют (доступность rclone
    проверяется при разрешении целей).

    Raises:
        CommandError: При STORAGE_TYPE=s3 не задана одна из переменных
            MEDIA_S3_VARS.
    """
    if not is_s3():
        return
    missing = [name for name in MEDIA_S3_VARS if not getattr(settings, name)]
    if missing:
        msg = f"переменная {', '.join(missing)} не задана в .env (требуется при STORAGE_TYPE=s3)"
        raise CommandError(msg)
