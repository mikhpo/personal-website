/**
 * Сервис навигации браузера.
 *
 * Вынесен в отдельный модуль для возможности подмены в тестах:
 * jsdom не реализует навигацию и не позволяет мокать window.location.
 */

/**
 * Выполнить переход на указанный URL полной загрузкой страницы.
 *
 * @param {string} url - URL для перехода
 */
const navigateTo = (url) => {
  window.location.assign(url);
};

export { navigateTo };
