import os


def str_to_bool(val: str):
    """
    Адаптированная имплементация функции strtobool из стандартной библиотеки distutils.
    """
    if not val:
        return False
    value = val.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif value in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"Неверное значение аргумента {val}")


def is_running_in_container():
    """
    Проверяет, запущено ли приложение внутри контейнера и возвращает логическое значение.
    """
    if os.path.exists("/proc/1/cgroup"):
        return True
    else:
        return False
