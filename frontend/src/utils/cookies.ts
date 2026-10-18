/**
 * Утилиты для работы с cookies.
 *
 * Предоставляет функции для чтения cookies, используемые в первую очередь
 * для работы с CSRF защитой Django.
 */

/**
 * Читает значение cookie по имени.
 *
 * @example
 * const csrfToken = getCookie('csrftoken');
 */
export const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const part = parts.pop();
    return part !== undefined ? (part.split(';').shift() ?? null) : null;
  }
  return null;
};

/**
 * Получает CSRF токен из cookie.
 *
 * Короткая функция-обёртка для получения csrftoken.
 *
 * @example
 * const token = getCsrfToken();
 */
export const getCsrfToken = (): string | null => getCookie('csrftoken');
