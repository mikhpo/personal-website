def str_to_bool(val: str):
    """
    Адаптированная имплементация функции strtobool из стандартной библиотеки distutils.
    """
    if not val:
        return 0
    value = val.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif value in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError(f"Неверное значение аргумента {val}")
