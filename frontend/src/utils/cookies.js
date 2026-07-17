/**
 * Утилиты для работы с cookies.
 *
 * Предоставляет функции для чтения cookies, используемые в первую очередь
 * для работы с CSRF защитой Django.
 */

/**
 * Читает значение cookie по имени.
 *
 * @param {string} name - Имя cookie
 * @return {string|null} Значение cookie или null
 *
 * @example
 * const csrfToken = getCookie('csrftoken');
 */
export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

/**
 * Получает CSRF токен из cookie.
 *
 * Короткая функция-обёртка для получения csrftoken.
 *
 * @return {string|null} CSRF токен или null
 *
 * @example
 * const token = getCsrfToken();
 */
export const getCsrfToken = () => getCookie('csrftoken');
