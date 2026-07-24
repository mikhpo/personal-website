/**
 * Тесты для API клиента.
 *
 * Проверяют работу ApiError класса и методов ApiClient,
 * включая обработку CSRF токенов, HTTP методов и ошибок.
 */

import { ApiError, default as api } from './api';

describe('api', () => {
  beforeEach(() => {
    // Очищаем моки перед каждым тестом
    jest.clearAllMocks();

    // Настраиваем mock для document.cookie
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    });

    // Устанавливаем тестовый CSRF токен
    document.cookie = 'csrftoken=test-csrf-token';
  });

  afterEach(() => {
    // Очищаем cookie после каждого теста
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  });

  /**
   * Тесты для класса ApiError.
   */
  describe('ApiError', () => {
    test('создаёт экземпляр ошибки с правильными свойствами', () => {
      const error = new ApiError(404, 'Not Found', { detail: 'Resource not found' });

      expect(error).toBeInstanceOf(Error);
      expect(error.name).toBe('ApiError');
      expect(error.status).toBe(404);
      expect(error.message).toBe('Not Found');
      expect(error.data).toEqual({ detail: 'Resource not found' });
    });

    test('isAuthError возвращает true для 401 статуса', () => {
      const error = new ApiError(401, 'Unauthorized');
      expect(error.isAuthError()).toBe(true);
      expect(error.isForbidden()).toBe(false);
      expect(error.isNotFound()).toBe(false);
    });

    test('isForbidden возвращает true для 403 статуса', () => {
      const error = new ApiError(403, 'Forbidden');
      expect(error.isAuthError()).toBe(false);
      expect(error.isForbidden()).toBe(true);
      expect(error.isNotFound()).toBe(false);
    });

    test('isNotFound возвращает true для 404 статуса', () => {
      const error = new ApiError(404, 'Not Found');
      expect(error.isAuthError()).toBe(false);
      expect(error.isForbidden()).toBe(false);
      expect(error.isNotFound()).toBe(true);
    });

    test('isServerError возвращает true для 5xx статусов', () => {
      const error500 = new ApiError(500, 'Internal Server Error');
      const error503 = new ApiError(503, 'Service Unavailable');
      const error400 = new ApiError(400, 'Bad Request');

      expect(error500.isServerError()).toBe(true);
      expect(error503.isServerError()).toBe(true);
      expect(error400.isServerError()).toBe(false);
    });

    test('сохраняет дополнительные данные об ошибке', () => {
      const errorData = {
        detail: 'Validation error',
        fields: { email: 'Invalid email' },
      };
      const error = new ApiError(400, 'Bad Request', errorData);

      expect(error.data).toEqual(errorData);
    });
  });

  /**
   * Тесты для метода GET.
   */
  describe('get', () => {
    test('успешно выполняет GET запрос и парсит JSON', async () => {
      const mockData = { id: 1, name: 'Test' };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.get('/api/test/');

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith('/api/test/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    test('пробрасывает дополнительные опции в fetch', async () => {
      const mockData = { results: [] };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      await api.get('/api/test/', {
        headers: { 'X-Custom-Header': 'value' },
      });

      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'GET',
        headers: expect.objectContaining({
          'X-Custom-Header': 'value',
        }),
      });
    });

    test('выбрасывает ApiError при неуспешном ответе', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
      });

      await expect(api.get('/api/notfound/')).rejects.toThrow('Ошибка загрузки: 404');
      await expect(api.get('/api/notfound/')).rejects.toMatchObject({
        status: 404,
        name: 'ApiError',
      });
    });
  });

  /**
   * Тесты для метода POST.
   */
  describe('post', () => {
    test('успешно выполняет POST запрос с CSRF токеном', async () => {
      const mockData = { id: 1, created: true };
      const postData = { title: 'Test', content: 'Content' };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.post('/api/test/', postData);

      expect(result).toEqual(mockData);
      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'test-csrf-token',
        },
        body: JSON.stringify(postData),
      });
    });

    test('выполняет POST запрос без CSRF токена когда withCsrf=false', async () => {
      const mockData = { success: true };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      await api.post('/api/test/', {}, { withCsrf: false });

      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1].headers).not.toHaveProperty('X-CSRFToken');
    });

    test('выбрасывает ApiError при ошибке POST', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 400,
      });

      await expect(api.post('/api/test/', {})).rejects.toThrow('Ошибка отправки: 400');
    });
  });

  /**
   * Тесты для метода POST с FormData.
   */
  describe('postForm', () => {
    test('успешно выполняет POST запрос с FormData и CSRF токеном', async () => {
      const mockData = { id: 1, uploaded: true };
      const formData = new FormData();
      formData.append('file', 'file-content');

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.postForm('/api/upload/', formData);

      expect(result).toEqual(mockData);
      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'POST',
        headers: {
          'X-CSRFToken': 'test-csrf-token',
        },
        body: formData,
      });
      // FormData не должен иметь Content-Type заголовок (устанавливается браузером)
      expect(fetchCall[1].headers).not.toHaveProperty('Content-Type');
    });

    test('выполняет POST с FormData без CSRF токена когда withCsrf=false', async () => {
      const formData = new FormData();
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      });

      await api.postForm('/api/upload/', formData, { withCsrf: false });

      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1].headers).not.toHaveProperty('X-CSRFToken');
    });
  });

  /**
   * Тесты для метода PUT.
   */
  describe('put', () => {
    test('успешно выполняет PUT запрос с CSRF токеном', async () => {
      const mockData = { id: 1, updated: true };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.put('/api/test/1/', { name: 'Updated' });

      expect(result).toEqual(mockData);
      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'test-csrf-token',
        },
      });
    });

    test('выбрасывает ApiError при ошибке PUT', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 403,
      });

      await expect(api.put('/api/test/1/', {})).rejects.toThrow('Ошибка обновления: 403');
    });
  });

  /**
   * Тесты для метода PATCH.
   */
  describe('patch', () => {
    test('успешно выполняет PATCH запрос с CSRF токеном', async () => {
      const mockData = { id: 1, patched: true };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.patch('/api/test/1/', { status: 'active' });

      expect(result).toEqual(mockData);
      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'test-csrf-token',
        },
      });
    });

    test('выбрасывает ApiError при ошибке PATCH', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
      });

      await expect(api.patch('/api/test/1/', {})).rejects.toThrow(
        'Ошибка частичного обновления: 404'
      );
    });
  });

  /**
   * Тесты для метода DELETE.
   */
  describe('delete', () => {
    test('успешно выполняет DELETE запрос с CSRF токеном и возвращает null для 204', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 204,
        json: async () => null,
      });

      const result = await api.delete('/api/test/1/');

      expect(result).toBeNull();
      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1]).toMatchObject({
        method: 'DELETE',
        headers: {
          'X-CSRFToken': 'test-csrf-token',
        },
      });
    });

    test('возвращает JSON ответ для DELETE без 204 статуса', async () => {
      const mockData = { deleted: true };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

      const result = await api.delete('/api/test/1/');

      expect(result).toEqual(mockData);
    });

    test('выполняет DELETE без CSRF токена когда withCsrf=false', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 204,
        json: async () => null,
      });

      await api.delete('/api/test/1/', { withCsrf: false });

      const fetchCall = global.fetch.mock.calls[0];
      expect(fetchCall[1].headers).not.toHaveProperty('X-CSRFToken');
    });

    test('выбрасывает ApiError при ошибке DELETE', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 403,
      });

      await expect(api.delete('/api/test/1/')).rejects.toThrow('Ошибка удаления: 403');
    });
  });
});
