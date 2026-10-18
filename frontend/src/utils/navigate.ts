/**
 * Переход на указанный URL полной перезагрузкой страницы.
 *
 * Вынесен в отдельный модуль, чтобы компоненты оставались тестируемыми:
 * jsdom не реализует навигацию, а модуль в тестах подменяется через jest.mock.
 */
export const navigateTo = (url: string): void => {
  window.location.href = url;
};

export default navigateTo;
