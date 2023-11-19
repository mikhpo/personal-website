import os

from django.conf import settings
from django.test import SimpleTestCase

from utils import list_file_paths


class ListFilePathTests(SimpleTestCase):
    """
    Тестирование утилиты поиска абсолютных путей тестовых фотографий.
    """

    def test_paths_exist(self):
        """
        Проверить, что возвращенные пути существуют.
        """
        image_paths_list = list_file_paths(settings.TEST_IMAGES_DIR)
        self.assertIsInstance(image_paths_list, list)
        for image_path in image_paths_list:
            self.assertTrue(os.path.exists(image_path))
