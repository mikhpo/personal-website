"""Определение параметров хранения загружаемых файлов."""

import shutil
import uuid
from io import BytesIO
from pathlib import Path
from typing import IO, Any, Callable, Union

from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, storages
from django.utils.text import slugify
from faker_file.storages.filesystem import FileSystemStorage as FakerFileSystemStorage  # type: ignore[import-untyped]
from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import-untyped]


class BaseStorageMixin:
    """Базовый миксин для хранилищ с реализацией общих методов."""

    def _get_relative_name(self, name: str) -> str:
        """
        Получение относительного имени файла, исключая base_location из пути.

        Args:
            name (str): Исходное имя файла (может быть абсолютным путем).

        Returns:
            str: Относительное имя файла.
        """
        # Преобразуем name в строку, если это Path
        if isinstance(name, Path):
            name = str(name)

        # Преобразуем base_location в строку, если это Path
        base_location = getattr(self, "base_location", "")
        if isinstance(base_location, Path):
            base_location = str(base_location)

        # Проверяем, что base_location является частью имени файла.
        if base_location and name.startswith(base_location):
            # Разделяем путь по base_location и берем вторую часть.
            parts = name.split(base_location, 1)
            if len(parts) > 1:
                # Возвращаем вторую часть без ведущих слэшей.
                return parts[1].lstrip("/")

        # Если base_location пустая строка, удаляем начальный слэш из имени файла.
        elif base_location == "" and name.startswith("/"):
            return name.lstrip("/")
        return name

    def _normalize_s3_path(self, name: str) -> str:
        """
        Нормализует путь для S3, извлекая относительный путь из полного S3 URI.

        Args:
            name (str): Исходное имя файла (может быть S3 URI или относительным путем).

        Returns:
            str: Нормализованный относительный путь.
        """
        # Преобразуем name в строку, если это Path
        if isinstance(name, Path):
            name = str(name)

        # Если имя файла начинается с s3://, извлекаем относительный путь
        if name.startswith("s3://"):
            # Формат: s3://bucket_name/path/to/file
            # Нам нужен только path/to/file
            return name.split("/", 3)[3]
        return name


class CustomFileSystemStorage(BaseStorageMixin, FileSystemStorage):
    """Расширенная система хранения для локальной файловой системы."""

    def save(self, name: str | None, content: IO[Any] | bytes, max_length: int | None = None) -> str:
        """
        Сохраняет файл в хранилище.

        Args:
            name: Имя файла.
            content: Содержимое файла (может быть файловым объектом или байтами).

        Returns:
            Имя сохраненного файла.
        """
        if not name:
            msg = "Необходимо передать имя файла"
            raise ValueError(msg)
        relative_name = self._get_relative_name(name)
        relative_name = self._normalize_s3_path(relative_name)

        # Если content - это байты, преобразуем их в файловый объект
        if isinstance(content, bytes):
            content = ContentFile(content)
        return super().save(relative_name, content, max_length)

    def listdir(self, path: str) -> tuple[list[str], list[str]]:
        """
        Получить список файлов и подкаталогов в заданной директории.

        Args:
            path (str): Путь к директории.

        Returns:
            tuple[list[str], list[str]]: Кортеж из двух списков: файлов и подкаталогов.
        """
        # Получаем относительное имя файла
        relative_path = self._get_relative_name(path)

        # Получаем абсолютный путь
        abs_path = self.path(relative_path)

        # Получаем список файлов и подкаталогов
        try:
            path_obj = Path(abs_path)
            entries = path_obj.iterdir()
        except OSError:
            # Если директория не существует или недоступна, возвращаем пустые списки
            return ([], [])

        files = []
        dirs = []

        for entry in entries:
            if entry.is_file():
                files.append(entry.name)
            elif entry.is_dir():
                dirs.append(entry.name)

        return (files, dirs)

    def path(self, name: str) -> str:
        """
        Возвращает абсолютный путь к файлу.

        Args:
            name: Имя файла.

        Returns:
            Абсолютный путь к файлу.
        """
        relative_name = self._get_relative_name(name)
        return str(Path(self.location).joinpath(relative_name))

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """Переопределенный метод возвращения доступного имени файла с учетом обязательной перезаписи файла."""
        relative_name = self._get_relative_name(name)
        if self.exists(relative_name):
            self.delete(relative_name)
        return super().get_available_name(relative_name, max_length)

    def delete(self, name: str, missing_ok: bool = True) -> None:  # noqa: FBT001, FBT002
        """Удалить файл."""
        relative_name = self._get_relative_name(name)
        Path(self.path(relative_name)).unlink(missing_ok=missing_ok)

    def mkdir(
        self,
        path: Union[str, Path],
        parents: bool = True,  # noqa: FBT001, FBT002
        exist_ok: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        """
        Создание директории по указанному пути, включая все необходимые родительские директории.

        Args:
            path (Union[str, Path]): Путь к создаваемой директории.
            parents (bool): Если True, создает все необходимые родительские директории.
            exist_ok (bool): Если True, не вызывает исключение, если директория уже существует.

        Raises:
            OSError: Если создание директории не удалось.
        """
        relative_path = self._get_relative_name(str(path))
        abs_path = self.path(relative_path)
        Path(abs_path).mkdir(parents=parents, exist_ok=exist_ok)

    def is_dir(self, path: Union[str, Path]) -> bool:
        """
        Проверяет, является ли указанный путь директорией.

        Args:
            path (Union[str, Path]): Путь для проверки.

        Returns:
            bool: True, если путь является директорией, иначе False.
        """
        relative_path = self._get_relative_name(str(path))
        abs_path = self.path(relative_path)
        return Path(abs_path).is_dir()

    def rmdir(self, path: Union[str, Path]) -> None:
        """
        Удаляет пустую директорию по указанному пути.

        Args:
            path (Union[str, Path]): Путь к удаляемой директории.

        Raises:
            OSError: Если директория не пуста или не существует.
        """
        relative_path = self._get_relative_name(str(path))
        abs_path = self.path(relative_path)
        Path(abs_path).rmdir()

    def rmtree(self, path: Union[str, Path], ignore_errors: bool = True) -> None:  # noqa: FBT001, FBT002
        """
        Рекурсивно удаляет директорию и всё её содержимое.

        Args:
            path (Union[str, Path]): Путь к удаляемой директории.
            ignore_errors (bool): Если True, игнорировать ошибки удаления.
                                  По умолчанию True.
        """
        relative_path = self._get_relative_name(str(path))
        abs_path = self.path(relative_path)
        shutil.rmtree(abs_path, ignore_errors=ignore_errors)

    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Копирование файла с исходного пути в целевой.

        Args:
            src (Union[str, Path]): Исходный путь к файлу.
            dst (Union[str, Path]): Путь назначения для файла.

        Raises:
            FileNotFoundError: Если исходный файл не найден.
        """
        # Получаем абсолютные пути для исходного и целевого файлов
        src_relative = self._get_relative_name(str(src))
        dst_relative = self._get_relative_name(str(dst))
        src_path = Path(self.path(src_relative))
        dst_path = Path(self.path(dst_relative))

        if not src_path.exists():
            error_message = f"Файл {src_path} не найден."
            raise FileNotFoundError(error_message)

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)

    def save_document(self, name: str, save_func: Callable[[BytesIO], None]) -> str:
        """
        Сохраняет документ, созданный функцией save_func, в хранилище.

        Args:
            name: Имя файла.
            save_func: Функция, которая записывает данные в поток.

        Returns:
            Имя сохранённого файла.
        """
        relative_name = self._get_relative_name(name)
        with BytesIO() as stream:
            save_func(stream)
            stream.seek(0)
            return self.save(relative_name, stream)

    def read_bytes(self, name: str) -> bytes:
        """
        Читает содержимое файла в виде байтов.

        Args:
            name: Имя файла.

        Returns:
            Содержимое файла в виде байтов.
        """
        relative_name = self._get_relative_name(name)
        abs_path = Path(self.path(relative_name))
        return abs_path.read_bytes()

    def joinpath(self, *paths: Union[str, Path]) -> str:
        """
        Объединяет пути в один путь.

        Args:
            *paths: Пути для объединения.

        Returns:
            Объединенный путь как строка.
        """
        path = Path(*paths)
        return str(path)

    def name(self, path: Union[str, Path]) -> str:
        """
        Возвращает имя файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Имя файла.
        """
        return Path(path).name

    def stem(self, path: Union[str, Path]) -> str:
        """
        Возвращает имя файла без расширения из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Имя файла без расширения.
        """
        return Path(path).stem

    def suffix(self, path: Union[str, Path]) -> str:
        """
        Возвращает расширение файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Расширение файла.
        """
        return Path(path).suffix

    def with_suffix(self, path: Union[str, Path], suffix: str) -> str:
        """
        Возвращает путь к файлу с измененным расширением.

        Args:
            path (Union[str, Path]): Путь к файлу.
            suffix (str): Новое расширение файла.

        Returns:
            Путь к файлу с измененным расширением.
        """
        return str(Path(path).with_suffix(suffix))

    def parent(self, path: Union[str, Path]) -> str:
        """
        Возвращает родительский каталог файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Родительский каталог файла.
        """
        parent_path = Path(path).parent
        # Если родительский путь является текущей директорией, возвращаем пустую строку
        if parent_path == Path():
            return ""
        return str(parent_path)

    def replace(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Переименование файла: заменяет файл по пути src на файл по пути dst.

        Args:
            src (Union[str, Path]): Путь к исходному файлу.
            dst (Union[str, Path]): Путь к целевому файлу.
        """
        relative_src = self._get_relative_name(str(src))
        relative_dst = self._get_relative_name(str(dst))
        abs_src = self.path(relative_src)
        abs_dst = self.path(relative_dst)
        Path(abs_src).replace(abs_dst)

    def relative_to(self, path: Union[str, Path], other: Union[str, Path]) -> str:
        """
        Вычисляет относительный путь от 'other' к 'path'.

        Args:
            path (Union[str, Path]): Путь, для которого нужно вычислить относительный путь.
            other (Union[str, Path]): Базовый путь.

        Returns:
            str: Относительный путь от 'other' к 'path'.
        """
        path_obj = Path(path)
        other_obj = Path(other)
        relative_path = path_obj.relative_to(other_obj)
        # Если относительный путь является текущей директорией, возвращаем пустую строку
        if relative_path == Path():
            return ""
        return str(relative_path)

    def is_absolute(self, path: Union[str, Path]) -> bool:
        """
        Проверяет, является ли путь абсолютным.

        Args:
            path (Union[str, Path]): Путь для проверки.

        Returns:
            bool: True, если путь абсолютный, иначе False.
        """
        return Path(path).is_absolute()


class CustomS3Storage(BaseStorageMixin, S3Boto3Storage):
    """Расширенная S3 система хранения с дополнительными методами для работы с файлами."""

    def save(self, name: str, content: Any, *args, **kwargs) -> str:  # noqa: ANN401
        """
        Сохраняет файл в S3 хранилище.

        Args:
            name: Имя файла.
            content: Содержимое файла (может быть файловым объектом или байтами).

        Returns:
            Имя сохраненного файла.
        """
        relative_name = self._get_relative_name(name)
        relative_name = self._normalize_s3_path(relative_name)

        # Если content - это байты, преобразуем их в файловый объект
        if isinstance(content, bytes):
            content = ContentFile(content)

        # Используем родительский метод save класса S3Boto3Storage для загрузки файла в S3
        return super().save(relative_name, content, *args, **kwargs)

    def listdir(self, path: str) -> tuple[list[str], list[str]]:
        """
        Получить список файлов и подкаталогов в заданной директории.

        Args:
            path (str): Путь к директории.

        Returns:
            tuple[list[str], list[str]]: Кортеж из двух списков: файлов и подкаталогов.
        """
        # Получаем относительное имя файла
        relative_path = self._get_relative_name(path)
        relative_path = self._normalize_s3_path(relative_path)

        # Добавляем завершающий слэш, чтобы получить список файлов в директории
        if relative_path and not relative_path.endswith("/"):
            relative_path += "/"

        return self._listdir_paginated(relative_path)

    def _listdir_paginated(self, prefix: str) -> tuple[list[str], list[str]]:
        """
        Получить список файлов и подкаталогов с использованием пагинации.

        Args:
            prefix (str): Префикс для поиска объектов.

        Returns:
            tuple[list[str], list[str]]: Кортеж из двух списков: файлов и подкаталогов.
        """
        try:
            paginator = self.connection.meta.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")

            files = []
            dirs = []

            for page in pages:
                # Обрабатываем директории (представляем их как пустые объекты с суффиксом '/')
                if "CommonPrefixes" in page:
                    for prefix_info in page["CommonPrefixes"]:
                        # Извлекаем имя директории из префикса
                        dir_name = prefix_info["Prefix"].rstrip("/")
                        if dir_name:
                            # Извлекаем последнюю часть пути как имя директории
                            dir_name = dir_name.split("/")[-1]
                            dirs.append(dir_name)

                # Обрабатываем файлы
                if "Contents" in page:
                    for obj in page["Contents"]:
                        # Получаем путь к объекту
                        obj_key = obj["Key"]
                        # Извлекаем имя файла из ключа
                        file_name = obj_key.split("/")[-1]
                        # Пропускаем пустые имена файлов (это может быть директория)
                        if file_name:
                            files.append(file_name)

        except ClientError:
            # Если произошла ошибка (например, директория не существует), возвращаем пустые списки
            return ([], [])
        else:
            return (files, dirs)

    def __init__(self, *args, **kwargs) -> None:
        """Инициализация хранилища с клиентом Minio."""
        super().__init__(*args, **kwargs)

    @property
    def base_location(self) -> str:
        """Возвращает базовое расположение файлов в хранилище."""
        # По аналогии с FileSystemStorage, base_location должен быть равен location
        # В S3Storage location - это обычный атрибут, который устанавливается при инициализации
        return self.location

    @property
    def base_url(self) -> str | None:
        """Возвращает базовый URL для доступа к файлам."""
        # Если задан custom_domain, используем его/
        if self.custom_domain:
            protocol = getattr(self, "url_protocol", "https:")
            return f"{protocol}//{self.custom_domain}/"

        # Если задан endpoint_url и bucket_name, формируем URL/
        if self.endpoint_url and self.bucket_name:
            # Убираем завершающий слэш у endpoint_url
            endpoint = self.endpoint_url.rstrip("/")
            return f"{endpoint}/{self.bucket_name}/"

        # Если ничего не задано, возвращаем None
        return None

    def path(self, name: str) -> str:
        """
        Возвращает строковое представление пути к файлу.

        Args:
            name: Имя файла.

        Returns:
            Строковое представление пути.
        """
        # Если имя файла уже начинается с s3://, возвращаем его как есть
        if name.startswith("s3://"):
            return name

        bucket_name = self.bucket_name if hasattr(self, "bucket_name") else ""
        location = self.base_location.lstrip("/")
        name = name.lstrip("/")
        if location:
            return f"s3://{bucket_name}/{location}/{name}"
        return f"s3://{bucket_name}/{name}"

    def get_modified_time(self, name: str):  # type: ignore[override]  # noqa: ANN201
        """
        Возвращает время последнего изменения файла.

        Args:
            name: Имя файла.

        Returns:
            Время последнего изменения файла.

        Raises:
            FileNotFoundError: Если файл не существует.
        """
        from django.utils import timezone

        relative_name = self._get_relative_name(name)
        relative_name = self._normalize_s3_path(relative_name)

        try:
            obj = self.connection.Object(self.bucket_name, relative_name)
            # Получаем время последнего изменения из метаданных объекта
            modified_time = obj.last_modified
            # Преобразуем в локальное время Django
            if timezone.is_naive(modified_time):
                modified_time = timezone.make_aware(modified_time)
        except Exception as e:
            # Проверяем, является ли исключение связано с отсутствием файла
            if "404" in str(e) or "NoSuchKey" in str(e) or "Not Found" in str(e):
                raise FileNotFoundError(relative_name) from e
            raise
        else:
            return modified_time

    def save_document(self, name: str, save_func: Callable[[BytesIO], None]) -> str:
        """
        Сохраняет документ, созданный функцией save_func, в хранилище.

        Args:
            name: Имя файла.
            save_func: Функция, которая записывает данные в поток.

        Returns:
            Имя сохранённого файла.
        """
        relative_name = self._get_relative_name(name)
        with BytesIO() as stream:
            save_func(stream)
            stream.seek(0)
            return self.save(relative_name, stream)

    def mkdir(
        self,
        path: Union[str, Path],
        parents: bool = True,  # noqa: FBT001, FBT002
        exist_ok: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        """
        Создание директории по указанному пути.
        Для S3 хранилища это операция не требуется, так как S3 не имеет иерархической структуры каталогов.

        Args:
            path (Union[str, Path]): Путь к создаваемой директории.
            parents (bool): Если True, создает все необходимые родительские директории.
            exist_ok (bool): Если True, не вызывает исключение, если директория уже существует.
                             Параметр добавлен для совместимости интерфейса.
        """
        # В S3 нет необходимости создавать директории, так как они создаются автоматически
        # при загрузке объектов. Этот метод добавлен для совместимости интерфейса.

    def is_dir(self, path: Union[str, Path]) -> bool:  # type: ignore[override]  # noqa: ARG002
        """
        Проверяет, является ли указанный путь директорией.
        Для S3 хранилища это всегда возвращает False, так как S3 не имеет иерархической структуры каталогов.

        Args:
            path (Union[str, Path]): Путь для проверки.

        Returns:
            bool: Всегда False для S3 хранилища.
        """
        # В S3 нет директорий в традиционном смысле, поэтому всегда возвращаем False
        # Этот метод добавлен для совместимости интерфейса.
        return False

    def rmdir(self, path: Union[str, Path]) -> None:
        """
        Удаляет пустую директорию по указанному пути.
        Для S3 хранилища это операция не требуется, так как S3 не имеет иерархической структуры каталогов.

        Args:
            path (Union[str, Path]): Путь к удаляемой директории.
        """
        # В S3 нет необходимости удалять директории, так как они удаляются автоматически
        # при удалении всех объектов в них. Этот метод добавлен для совместимости интерфейса.

    def rmtree(self, path: Union[str, Path], ignore_errors: bool = True) -> None:  # noqa: FBT001, FBT002
        """
        Рекурсивно удаляет директорию и всё её содержимое.
        Для S3 это означает удаление всех объектов с указанным префиксом.

        Args:
            path (Union[str, Path]): Путь к удаляемой директории.
            ignore_errors (bool): Если True, игнорировать ошибки удаления.
                                  По умолчанию True.
        """
        try:
            relative_path = self._get_relative_name(str(path)).rstrip("/") + "/"
            relative_path = self._normalize_s3_path(relative_path)

            # Получаем список всех объектов с данным префиксом
            paginator = self.connection.meta.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=relative_path)

            # Собираем все ключи для удаления
            delete_keys = []
            for page in pages:
                if "Contents" in page:
                    delete_keys.extend({"Key": obj["Key"]} for obj in page["Contents"])

            # Удаляем все объекты
            if delete_keys:
                # S3 позволяет удалять до 1000 объектов за один запрос
                for i in range(0, len(delete_keys), 1000):
                    batch = delete_keys[i : i + 1000]
                    self.connection.meta.client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={"Objects": batch},
                    )
        except Exception as error:
            if not ignore_errors:
                error_message = f"Не удалось удалить директорию {path}: {error}"
                raise OSError(error_message) from error

    def joinpath(self, *paths: Union[str, Path]) -> str:
        """
        Объединяет пути в один путь.

        Args:
            *paths: Пути для объединения.

        Returns:
            Объединенный путь как строка.
        """
        # Преобразуем все пути в строки и объединяем их.
        str_paths = [str(path).strip("/") for path in paths if path]
        return "/".join(str_paths)

    def name(self, path: Union[str, Path]) -> str:
        """
        Возвращает имя файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Имя файла.
        """
        # Для S3 путь - это просто строка, из которой мы извлекаем имя файла
        path_str = str(path)
        return path_str.split("/")[-1]

    def stem(self, path: Union[str, Path]) -> str:
        """
        Возвращает имя файла без расширения из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Имя файла без расширения.
        """
        # Получаем имя файла и убираем расширение
        filename = self.name(path)
        return ".".join(filename.split(".")[:-1]) if "." in filename else filename

    def suffix(self, path: Union[str, Path]) -> str:
        """
        Возвращает расширение файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Расширение файла.
        """
        # Получаем имя файла и извлекаем расширение
        filename = self.name(path)
        return "." + filename.split(".")[-1] if "." in filename else ""

    def with_suffix(self, path: Union[str, Path], suffix: str) -> str:
        """
        Возвращает путь к файлу с измененным расширением.

        Args:
            path (Union[str, Path]): Путь к файлу.
            suffix (str): Новое расширение файла.

        Returns:
            Путь к файлу с измененным расширением.
        """
        # Получаем путь как строку
        path_str = str(path)
        # Разделяем путь на части по "/"
        parts = path_str.split("/")
        # Получаем имя файла (последняя часть пути)
        filename = parts[-1]
        # Убираем старое расширение и добавляем новое
        new_filename = ".".join(filename.split(".")[:-1]) + suffix if "." in filename else filename + suffix
        # Заменяем имя файла в частях пути и объединяем обратно
        parts[-1] = new_filename
        return "/".join(parts)

    def parent(self, path: Union[str, Path]) -> str:
        """
        Возвращает родительский каталог файла из пути.

        Args:
            path (Union[str, Path]): Путь к файлу.

        Returns:
            Родительский каталог файла.
        """
        # Для S3 путь - это просто строка, из которой мы извлекаем родительский каталог
        path_str = str(path)
        return "/".join(path_str.split("/")[:-1])

    def replace(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Переименование файла: заменяет файл по пути src на файл по пути dst.
        Для S3 это означает копирование объекта с новым ключом и удаление старого.

        Args:
            src (Union[str, Path]): Путь к исходному файлу.
            dst (Union[str, Path]): Путь к целевому файлу.
        """
        # В S3 "переименование" - это копирование объекта с новым ключом и удаление старого
        # Получаем объекты источника и назначения
        src_key = self._get_relative_name(str(src))
        src_key = self._normalize_s3_path(src_key)
        dst_key = self._get_relative_name(str(dst))
        dst_key = self._normalize_s3_path(dst_key)

        try:
            # Копируем объект с новым ключом
            copy_source = {"Bucket": self.bucket_name, "Key": src_key}
            self.connection.meta.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dst_key,
            )
        except Exception as error:
            error_message = f"Не удалось скопировать файл из {src_key} в {dst_key}: {error}"
            raise ClientError(error_message) from error

        try:
            # Удаляем исходный объект
            self.connection.meta.client.delete_object(
                Bucket=self.bucket_name,
                Key=src_key,
            )
        except Exception as error:
            error_message = f"Не удалось удалить исходный файл {src_key}: {error}"
            raise ClientError(error_message) from error

    def delete(self, name: str, missing_ok: bool = True) -> None:  # noqa: FBT001, FBT002
        """
        Удалить файл.

        Args:
            name (str): Имя файла для удаления.
            missing_ok (bool): Если True, не вызывает исключение, если файл не существует.
        """
        relative_name = self._get_relative_name(name)
        relative_name = self._normalize_s3_path(relative_name)

        try:
            self.connection.meta.client.delete_object(
                Bucket=self.bucket_name,
                Key=relative_name,
            )
        except Exception:
            if not missing_ok:
                raise

    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Копирование файла с исходного пути в целевой.
        Если исходный файл находится в локальной файловой системе, загружаем его в S3.
        Если исходный файл находится в S3, копируем его с новым ключом.

        Args:
            src (Union[str, Path]): Исходный путь к файлу.
            dst (Union[str, Path]): Путь назначения для файла.
        """
        src_str = str(src)
        dst_key = self._get_relative_name(str(dst)).lstrip("/")
        dst_key = self._normalize_s3_path(dst_key)

        # Сначала проверяем, существует ли исходный файл в S3
        # Если да, то копируем его внутри S3
        if self.exists(src_str):
            # Исходный файл уже существует в S3, копируем его с новым ключом
            # Получаем ключ источника
            src_key = self._get_relative_name(src_str).lstrip("/")
            src_key = self._normalize_s3_path(src_key)

            # Копируем объект с новым ключом
            copy_source = {"Bucket": self.bucket_name, "Key": src_key}
            self.connection.meta.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dst_key,
            )
        # Файл не существует в S3, пытаемся обработать как локальный файл
        # Проверяем, является ли путь локальным (не начинается с s3://)
        # и существует ли файл в локальной файловой системе
        elif not src_str.startswith("s3://"):
            # Исходный файл в локальной файловой системе, загружаем его в S3
            src_path = Path(src_str)
            if not src_path.exists():
                error_message = f"Файл {src_path} не найден."
                raise FileNotFoundError(error_message)

            # Загружаем файл в S3
            self.save(dst_key, src_path.read_bytes())
        else:
            # Исходный файл указан как S3 путь, но не существует в S3
            # Это может быть ошибка в пути или неправильное использование метода
            error_message = f"Файл {src_str} не найден в S3 и не является локальным файлом."
            raise FileNotFoundError(error_message)

    def read_bytes(self, name: str) -> bytes:
        """
        Читает содержимое файла в виде байтов.

        Args:
            name: Имя файла.

        Returns:
            Содержимое файла в виде байтов.
        """
        relative_name = self._get_relative_name(name)
        relative_name = self._normalize_s3_path(relative_name)
        obj = self.connection.Object(self.bucket_name, relative_name)
        return obj.get()["Body"].read()

    def exists(self, name: str) -> bool:
        """
        Проверяет существование файла в S3 хранилище.

        Args:
            name: Имя файла.

        Returns:
            True, если файл существует, иначе False.
        """
        try:
            relative_name = self._get_relative_name(name)
            relative_name = self._normalize_s3_path(relative_name)
            self.connection.Object(self.bucket_name, relative_name).load()
        except Exception:  # noqa: BLE001
            return False
        else:
            return True

    def relative_to(self, path: Union[str, Path], other: Union[str, Path]) -> str:
        """
        Вычисляет относительный путь от 'other' к 'path'.

        Args:
            path (Union[str, Path]): Путь, для которого нужно вычислить относительный путь.
            other (Union[str, Path]): Базовый путь.

        Returns:
            str: Относительный путь от 'other' к 'path'.
        """
        # Для S3 пути являются строками, поэтому преобразуем их в Path для вычисления относительного пути
        from s3path import S3Path

        path_obj = S3Path(str(path))
        other_obj = S3Path(str(other))
        relative_path = path_obj.relative_to(other_obj)
        # Если относительный путь является текущей директорией, возвращаем пустую строку
        if str(relative_path) == ".":
            return ""
        return str(relative_path)

    def is_absolute(self, path: Union[str, Path]) -> bool:
        """
        Проверяет, является ли путь абсолютным.

        Args:
            path (Union[str, Path]): Путь для проверки.

        Returns:
            bool: True, если путь абсолютный, иначе False.
        """
        # Для совместимости с локальной файловой системой, проверяем абсолютность пути
        # как в классе FileSystemStorage
        path_str = str(path)
        return Path(path_str).is_absolute() or path_str.startswith("s3://")


class FakerFileStorageAdapter(FakerFileSystemStorage):
    """Адаптер для использования Django хранилища с faker_file."""

    def __init__(self, root_path: str = "", rel_path: str = "", *args, **kwargs) -> None:
        """Инициализация адаптера."""
        super().__init__(root_path, rel_path, *args, **kwargs)
        self.django_storage: StorageType = select_storage()
        if not root_path:
            self.root_path = self.django_storage.location

    def normalize_filename(self, filename: str) -> str:
        """Нормализовать имя файла."""
        return filename

    def abspath(self, filename: str) -> str:
        """Получить абсолютный путь к файлу."""
        return self.django_storage.path(filename)

    def exists(self, filename: str) -> bool:
        """Проверить существование файла."""
        return self.django_storage.exists(filename)

    def write(self, filename: str, data: bytes, *args, **kwargs) -> str:  # noqa: ARG002
        """Записать данные в файл."""
        content_file = ContentFile(data)
        return self.django_storage.save(filename, content_file)

    def read(self, filename: str, *args, **kwargs) -> bytes:  # noqa: ARG002
        """Прочитать данные из файла."""
        with self.django_storage.open(filename, "rb") as f:
            return f.read()

    def delete(self, filename: str) -> None:
        """Удалить файл."""
        return self.django_storage.delete(filename)

    def mkdir(self, path: Union[str, Path], *, parents: bool = True, exist_ok: bool = True) -> None:
        """
        Создание директории по указанному пути, включая все необходимые родительские директории.

        Args:
            path (Union[str, Path]): Путь к создаваемой директории.
            parents (bool): Если True, создает все необходимые родительские директории.
            exist_ok (bool): Если True, не вызывает исключение, если директория уже существует.
        """
        # Делегируем операцию mkdir хранилищу Django
        self.django_storage.mkdir(path, parents=parents, exist_ok=exist_ok)

    def generate_filename(self, extension: str, prefix: str = "", basename: str = "") -> str:  # type: ignore[override]
        """
        Генерирует имя файла с заданным расширением.

        Args:
            extension: Расширение файла.
            prefix: Префикс имени файла.
            basename: Базовое имя файла.

        Returns:
            Сгенерированное имя файла.
        """
        if not basename:
            basename = str(uuid.uuid4())[:8]

        filename = f"{prefix}{basename}.{extension}"
        # Нормализуем имя файла, убирая недопустимые символы
        return slugify(filename.replace(".", "-")) + f".{extension}"

    def write_text(self, filename: str, data: str, encoding: str = "utf-8") -> int:
        """
        Записывает текстовые данные в файл.

        Args:
            filename: Имя файла.
            data: Текстовые данные для записи.
            encoding: Кодировка текста.

        Returns:
            Количество записанных байтов.
        """
        content_file = ContentFile(data.encode(encoding))
        self.django_storage.save(filename, content_file)
        return len(data.encode(encoding))

    def write_bytes(self, filename: str, data: bytes) -> int:
        """
        Записывает байтовые данные в файл.

        Args:
            filename: Имя файла.
            data: Байтовые данные для записи.

        Returns:
            Количество записанных байтов.
        """
        content_file = ContentFile(data)
        self.django_storage.save(filename, content_file)
        return len(data)

    def unlink(self, filename: str) -> None:
        """
        Удаляет файл.

        Args:
            filename: Имя файла для удаления.
        """
        self.django_storage.delete(filename)

    def relpath(self, filename: str) -> str:
        """
        Возвращает относительный путь к файлу.

        Args:
            filename: Имя файла.

        Returns:
            Относительный путь к файлу.
        """
        return filename


StorageType = CustomFileSystemStorage | CustomS3Storage


def select_storage() -> StorageType:
    """Возвращает файловое хранилище по умолчанию."""
    # Для тестов использовать тестовое хранилище,
    # но не в том случае, если задано в явном виде использование S3.
    if settings.TEST and settings.STORAGE_TYPE != "s3":
        test_storage: CustomFileSystemStorage = storages["test"]  # type: ignore[assignment]
        return test_storage

    # Для S3 использовать хранилище S3
    if settings.STORAGE_TYPE == "s3":
        s3_storage: CustomS3Storage = storages["s3"]  # type: ignore[assignment]
        return s3_storage

    # Иначе использовать обычное файловое хранилище
    fs_storage: CustomFileSystemStorage = storages["filesystem"]  # type: ignore[assignment]
    return fs_storage
