/**
 * Переход на указанный URL полной перезагрузкой страницы.
 *
 * Вынесен в отдельный модуль, чтобы компоненты оставались тестируемыми:
 * jsdom не реализует навигацию, а модуль в тестах подменяется через jest.mock.
 *
 * @function navigateTo
 * @param {string} url - URL для перехода
 * @return {void}
 */
export const navigateTo = (url) => {
  window.location.href = url;
};

export default navigateTo;
