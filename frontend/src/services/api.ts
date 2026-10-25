/**
 * Базовый API клиент для выполнения HTTP запросов.
 *
 * Предоставляет унифицированный интерфейс для выполнения GET, POST, PUT, PATCH, DELETE запросов
 * с автоматической обработкой ошибок, CSRF токенов и JSON парсинга.
 */

import { getCsrfToken } from '../utils/cookies';

/** Опции запроса, принимаемые методами клиента. */
export interface RequestOptions {
  headers?: Record<string, string>;
  withCsrf?: boolean;
}

/**
 * Класс ошибки API.
 *
 * Расширяет стандартный Error для хранения дополнительной информации об ошибке API.
 */
export class ApiError extends Error {
  /** HTTP статус код */
  status: number;

  /** Дополнительные данные об ошибке */
  data: unknown;

  /**
   * Создает экземпляр ошибки API.
   */
  constructor(status: number, message: string, data: unknown = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }

  /**
   * Проверяет, является ли ошибкой авторизации (401).
   */
  isAuthError(): boolean {
    return this.status === 401;
  }

  /**
   * Проверяет, является ли ошибкой доступа (403).
   */
  isForbidden(): boolean {
    return this.status === 403;
  }

  /**
   * Проверяет, является ли ошибкой "не найдено" (404).
   */
  isNotFound(): boolean {
    return this.status === 404;
  }

  /**
   * Проверяет, является ли ошибкой сервера (5xx).
   */
  isServerError(): boolean {
    return this.status >= 500;
  }
}

/**
 * Базовый API клиент.
 */
class ApiClient {
  /** Базовые заголовки для всех запросов. */
  baseHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  /**
   * Выполняет запрос и разбирает ответ с единой обработкой ошибок.
   *
   * errorLabel подставляется в сообщение ("загрузки", "отправки" и т.д.),
   * чтобы сообщения методов клиента остались прежними.
   *
   * allowEmpty разрешает пустой ответ (204) для методов, чей контракт
   * допускает отсутствие тела; без него 204 выбрасывает ApiError - методы
   * с обязательным телом не возвращают тихий null.
   */
  private async request<T>(url: string, init: RequestInit, errorLabel: string, allowEmpty = false): Promise<T> {
    const response = await fetch(url, init);

    if (!response.ok) {
      throw new ApiError(response.status, `Ошибка ${errorLabel}: ${response.status}`);
    }

    // 204 No Content не имеет тела
    if (response.status === 204) {
      if (!allowEmpty) {
        throw new ApiError(response.status, `Ошибка ${errorLabel}: сервер вернул пустой ответ`);
      }
      return null as T;
    }

    return response.json();
  }

  /**
   * Собирает заголовки с CSRF токеном, когда он нужен методу.
   */
  private withCsrfHeaders(base: Record<string, string>, options: RequestOptions): Record<string, string> {
    const { withCsrf = true } = options;
    const headers: Record<string, string> = { ...base };
    if (withCsrf) {
      headers['X-CSRFToken'] = getCsrfToken() ?? '';
    }
    return headers;
  }

  /**
   * Выполняет GET запрос.
   *
   * @example
   * const data = await api.get('/api/blog/articles/');
   */
  async get<T>(url: string, options: RequestOptions = {}): Promise<T> {
    const headers = { ...this.baseHeaders, ...options.headers };
    return this.request<T>(url, { method: 'GET', headers, ...options }, 'загрузки');
  }

  /**
   * Выполняет POST запрос.
   *
   * @example
   * const data = await api.post('/api/blog/comments/', { article: 1, content: 'text' });
   */
  async post<T>(url: string, data: unknown, options: RequestOptions = {}): Promise<T> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({ ...this.baseHeaders }, options);

    return this.request<T>(
      url,
      {
        method: 'POST',
        headers: { ...headers, ...requestOptions.headers },
        body: JSON.stringify(data),
        ...requestOptions,
      },
      'отправки',
    );
  }

  /**
   * Выполняет POST запрос с FormData (для загрузки файлов).
   *
   * @example
   * const formData = new FormData();
   * formData.append('file', file);
   * const data = await api.postForm('/api/gallery/upload/', formData);
   */
  async postForm<T>(url: string, formData: FormData, options: RequestOptions = {}): Promise<T> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({}, options);

    return this.request<T>(
      url,
      {
        method: 'POST',
        headers: { ...headers, ...requestOptions.headers },
        body: formData,
        ...requestOptions,
      },
      'отправки',
    );
  }

  /**
   * Выполняет PUT запрос с FormData (для обновления объектов с файлами).
   *
   * @example
   * const formData = new FormData();
   * formData.append('title', 'Новый заголовок');
   * const data = await api.putForm('/api/blog/articles/1/', formData);
   */
  async putForm<T>(url: string, formData: FormData, options: RequestOptions = {}): Promise<T> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({}, options);

    return this.request<T>(
      url,
      {
        method: 'PUT',
        headers: { ...headers, ...requestOptions.headers },
        body: formData,
        ...requestOptions,
      },
      'обновления',
    );
  }

  /**
   * Выполняет PUT запрос.
   */
  async put<T>(url: string, data: unknown, options: RequestOptions = {}): Promise<T> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({ ...this.baseHeaders }, options);

    return this.request<T>(
      url,
      {
        method: 'PUT',
        headers: { ...headers, ...requestOptions.headers },
        body: JSON.stringify(data),
        ...requestOptions,
      },
      'обновления',
    );
  }

  /**
   * Выполняет PATCH запрос.
   */
  async patch<T>(url: string, data: unknown, options: RequestOptions = {}): Promise<T> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({ ...this.baseHeaders }, options);

    return this.request<T>(
      url,
      {
        method: 'PATCH',
        headers: { ...headers, ...requestOptions.headers },
        body: JSON.stringify(data),
        ...requestOptions,
      },
      'частичного обновления',
    );
  }

  /**
   * Выполняет DELETE запрос.
   *
   * @return Ответ от сервера или null для 204 No Content
   */
  async delete<T>(url: string, options: RequestOptions = {}): Promise<T | null> {
    const { withCsrf: _withCsrf, ...requestOptions } = options;
    const headers = this.withCsrfHeaders({}, options);

    return this.request<T>(
      url,
      {
        method: 'DELETE',
        headers: { ...headers, ...requestOptions.headers },
        ...requestOptions,
      },
      'удаления',
      true,
    );
  }
}

// Экспорт singleton экземпляра клиента
export default new ApiClient();
