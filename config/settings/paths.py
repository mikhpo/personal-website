'''Пути к файлам на сервере.'''
import os
from pathlib import Path

# Определяется абсолютный путь до текущей директории для того, чтобы далее в проекте везде использовались относительные пути.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Путь до интерпретатора Python.
PYTHON_PATH = os.path.join(BASE_DIR, '..', '.venv', 'bin', 'python')

# Путь до модуля manage.py.
MANAGE_PATH = os.path.join(BASE_DIR, 'manage.py')

# Настройки логирования.
LOG_FOLDER = os.path.join(BASE_DIR, 'logs') # папка для сохранения логов