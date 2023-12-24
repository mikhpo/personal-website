import os


def list_file_paths(files_dir: str):
    """
    Определить пути набора набора файлов в указанном каталоге.

    Аргументы:
        files_dir (str): путь до файлов.

    Возвращает:
        Список полных путей до файлов.
    """
    names = os.listdir(files_dir)
    paths = [os.path.join(files_dir, name) for name in names]
    file_paths = [path for path in paths if os.path.isfile(path)]
    return file_paths


def calculate_path_size(path: str) -> dict:
    """
    Определение размера файла или каталога по указанному пути
      с автоматическим определением единцы измерения.

    Аргументы:
        path (str): путь до файла или каталога.

    Возвращает:
        Словарь, содержащий значение, единицу измерения и сообщение. Например: \
        
            ```python
            {"value": 500, "unit": "КБ", "message": "500 КБ"}
            ```
    """
    units = ("Б", "КБ", "МБ", "ГБ", "ТБ")

    # Способ определения размера дампа зависит от типа пути: файл или каталог.
    if os.path.isdir(path):
        size = 0
        for path, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(path, file)
                size += os.path.getsize(filepath)
    else:
        size = os.path.getsize(path)

    # Определение единцы измерения размера дампа. Значение округляется до целого числа.
    for unit in units:
        if size < 1024:
            value = int(size)
            return {"value": value, "unit": unit, "message": f"{value} {unit}"}
        size /= 1024
