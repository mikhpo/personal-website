/**
 * Сервис навигации браузера.
 *
 * Вынесен в отдельный модуль для возможности подмены в тестах:
 * jsdom не реализует навигацию и не позволяет мокать window.location.
 */

/**
 * Выполнить переход на указанный URL полной загрузкой страницы.
 */
const navigateTo = (url: string): void => {
  window.location.assign(url);
};

export { navigateTo };
