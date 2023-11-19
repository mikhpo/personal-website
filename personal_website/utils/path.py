import os


def list_file_paths(files_dir: str):
    """
    Определить пути набора изображений на локальном диске.
    """
    file_names = os.listdir(files_dir)
    file_paths = [os.path.join(files_dir, file_name) for file_name in file_names]
    return file_paths
