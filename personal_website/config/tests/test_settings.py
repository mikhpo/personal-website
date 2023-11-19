from django.conf import settings
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    """
    Тесты настроек проекта.
    """

    def test_testing_mode(self):
        testing = settings.TEST
        self.assertTrue(testing)
