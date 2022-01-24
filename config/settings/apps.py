'''
Список установленных программ. После добавления программы в список Django будет автоматически искать их модули в виртуальном окружении и в каталоге проекта.
Программы в список нужно добавлять в следующем порядке:
2. Модули от проекта Django.
1. Модули для Django от сообщества.
3. Локальные приложения автора.
'''
DJANGO_PACKAGES = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]
COMMUNITY_PACKAGES = [
    'whitenoise.runserver_nostatic',
    'tinymce',
    'crispy_forms',
]
PROJECT_APPS = [
    'apps.accounts.apps.AccountsConfig',
    'apps.main.apps.MainConfig',
    'apps.blog.apps.BlogConfig',
    'apps.scripts.apps.ScriptsConfig',
]
INSTALLED_APPS = DJANGO_PACKAGES + COMMUNITY_PACKAGES + PROJECT_APPS