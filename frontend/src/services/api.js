/**
 * Базовый API клиент для выполнения HTTP запросов.
 *
 * Предоставляет унифицированный интерфейс для выполнения GET, POST, PUT, PATCH, DELETE запросов
 * с автоматической обработкой ошибок, CSRF токенов и JSON парсинга.
 */

import { getCsrfToken } from '../utils/cookies';

/**
 * Класс ошибки API.
 *
 * Расширяет стандартный Error для хранения дополнительной информации об ошибке API.
 *
 * @class
 * @extends Error
 */
class ApiError extends Error {
  /**
   * Создает экземпляр ошибки API.
   *
   * @param {number} status - HTTP статус код
   * @param {string} message - Сообщение об ошибке
   * @param {Object} [data=null] - Дополнительные данные об ошибке
   */
  constructor(status, message, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }

  /**
   * Проверяет, является ли ошибкой авторизации (401).
   * @return {boolean}
   */
  isAuthError() {
    return this.status === 401;
  }

  /**
   * Проверяет, является ли ошибкой доступа (403).
   * @return {boolean}
   */
  isForbidden() {
    return this.status === 403;
  }

  /**
   * Проверяет, является ли ошибкой "не найдено" (404).
   * @return {boolean}
   */
  isNotFound() {
    return this.status === 404;
  }

  /**
   * Проверяет, является ли ошибкой сервера (5xx).
   * @return {boolean}
   */
  isServerError() {
    return this.status >= 500;
  }
}

/**
 * Базовый API клиент.
 *
 * @class
 */
class ApiClient {
  /**
   * Базовые заголовки для всех запросов.
   * @type {Object}
   */
  baseHeaders = {
    'Content-Type': 'application/json',
  };

  /**
   * Выполняет GET запрос.
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {Object} [options.headers={}] - Дополнительные заголовки
   * @return {Promise<Object>} Ответ от сервера в формате JSON
   * @throws {ApiError} При ошибке HTTP запроса
   *
   * @example
   * const data = await api.get('/api/blog/articles/');
   */
  async get(url, options = {}) {
    const headers = { ...this.baseHeaders, ...options.headers };
    const response = await fetch(url, {
      method: 'GET',
      headers,
      ...options,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка загрузки: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Выполняет POST запрос.
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {Object} data - Данные для отправки
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {Object} [options.headers={}] - Дополнительные заголовки
   * @param {boolean} [options.withCsrf=true] - Добавлять ли CSRF токен
   * @return {Promise<Object>} Ответ от сервера в формате JSON
   * @throws {ApiError} При ошибке HTTP запроса
   *
   * @example
   * const data = await api.post('/api/blog/comments/', { article: 1, content: 'text' });
   */
  async post(url, data, options = {}) {
    const { withCsrf = true, ...requestOptions } = options;
    const headers = { ...this.baseHeaders };

    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken();
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { ...headers, ...requestOptions.headers },
      body: JSON.stringify(data),
      ...requestOptions,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка отправки: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Выполняет POST запрос с FormData (для загрузки файлов).
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {FormData} formData - Данные формы
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {boolean} [options.withCsrf=true] - Добавлять ли CSRF токен
   * @return {Promise<Object>} Ответ от сервера в формате JSON
   * @throws {ApiError} При ошибке HTTP запроса
   *
   * @example
   * const formData = new FormData();
   * formData.append('file', file);
   * const data = await api.postForm('/api/gallery/upload/', formData);
   */
  async postForm(url, formData, options = {}) {
    const { withCsrf = true, ...requestOptions } = options;
    const headers = {};

    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken();
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { ...headers, ...requestOptions.headers },
      body: formData,
      ...requestOptions,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка отправки: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Выполняет PUT запрос.
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {Object} data - Данные для отправки
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {boolean} [options.withCsrf=true] - Добавлять ли CSRF токен
   * @return {Promise<Object>} Ответ от сервера в формате JSON
   * @throws {ApiError} При ошибке HTTP запроса
   */
  async put(url, data, options = {}) {
    const { withCsrf = true, ...requestOptions } = options;
    const headers = { ...this.baseHeaders };

    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken();
    }

    const response = await fetch(url, {
      method: 'PUT',
      headers: { ...headers, ...requestOptions.headers },
      body: JSON.stringify(data),
      ...requestOptions,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка обновления: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Выполняет PATCH запрос.
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {Object} data - Данные для отправки
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {boolean} [options.withCsrf=true] - Добавлять ли CSRF токен
   * @return {Promise<Object>} Ответ от сервера в формате JSON
   * @throws {ApiError} При ошибке HTTP запроса
   */
  async patch(url, data, options = {}) {
    const { withCsrf = true, ...requestOptions } = options;
    const headers = { ...this.baseHeaders };

    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken();
    }

    const response = await fetch(url, {
      method: 'PATCH',
      headers: { ...headers, ...requestOptions.headers },
      body: JSON.stringify(data),
      ...requestOptions,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка частичного обновления: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Выполняет DELETE запрос.
   *
   * @async
   * @param {string} url - URL для запроса
   * @param {Object} [options={}] - Дополнительные опции запроса
   * @param {boolean} [options.withCsrf=true] - Добавлять ли CSRF токен
   * @return {Promise<Object|null>} Ответ от сервера или null для 204 No Content
   * @throws {ApiError} При ошибке HTTP запроса
   */
  async delete(url, options = {}) {
    const { withCsrf = true, ...requestOptions } = options;
    const headers = {};

    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken();
    }

    const response = await fetch(url, {
      method: 'DELETE',
      headers: { ...headers, ...requestOptions.headers },
      ...requestOptions,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка удаления: ${response.status}`);
    }

    // 204 No Content не имеет тела
    if (response.status === 204) {
      return null;
    }

    return response.json();
  }
}

// Экспорт singleton экземпляра клиента
export default new ApiClient();

// Экспорт класса ошибки для использования в компонентах
export { ApiError };
