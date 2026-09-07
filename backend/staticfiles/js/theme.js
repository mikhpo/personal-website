/*
 * Определяет тему сайта до первой отрисовки страницы, чтобы избежать мерцания светлой темой.
 *
 * Подключается в <head> base.html до стилей обычным тегом script - браузер выполняет
 * его синхронно во время парсинга, до применения CSS. Добавлять defer или async нельзя:
 * отложенное выполнение означает отрисовку в дефолтной светлой теме.
 *
 * Приоритет: явный выбор пользователя в localStorage (формат JSON из useLocalStorage),
 * затем системная тема (prefers-color-scheme), затем светлая.
 * Логика повторяет хук useTheme - при изменении приоритета править оба места.
 */
(function() {
  var theme = null;
  try {
    theme = JSON.parse(window.localStorage.getItem('theme'));
  } catch (error) {
    theme = null;
  }
  if (theme !== 'light' && theme !== 'dark') {
    theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }
  document.documentElement.setAttribute('data-bs-theme', theme);
})();
