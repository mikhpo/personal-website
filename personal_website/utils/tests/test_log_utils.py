import logging
import os

from django.test import SimpleTestCase, override_settings

from personal_website.utils import set_file_logger

temp_dir = os.getenv("TEMP_ROOT")
temp_logs_dir = os.path.join(temp_dir, "logs")


@override_settings(LOG_DIR=temp_logs_dir)
class LogUtilsTests(SimpleTestCase):
    """
    Тесты утилит логирования.
    """

    def test_set_file_logger(self):
        """
        Функция `set_file_logger` возвращает объект `Logger`,
        который содержит два обработчика.
        """
        logger = set_file_logger(__file__)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(len(logger.handlers), 2)
