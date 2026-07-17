/**
 * Сервис для работы с API галереи.
 *
 * Предоставляет методы для выполнения запросов к API галереи:
 * - Получение списка альбомов и фотографий
 * - Загрузка фотографий
 * - Работа с тегами
 */

import api from './api';

/**
 * Базовый URL для API галереи.
 * @type {string}
 */
const BASE_URL = '/api/gallery';

/**
 * Сервис для работы с галереей.
 * @namespace
 */
export const galleryService = {
  /**
   * Получает список альбомов.
   *
   * @async
   * @param {Object} [params={}] - Параметры запроса
   * @param {string} [params.page] - Номер страницы
   * @return {Promise<Object>} Объект со списком альбомов
   *
   * @example
   * const albums = await galleryService.getAlbums();
   */
  async getAlbums(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${BASE_URL}/albums/?${queryString}` : `${BASE_URL}/albums/`;
    return api.get(url);
  },

  /**
   * Получает детальную информацию об альбоме.
   *
   * @async
   * @param {number} id - ID альбома
   * @return {Promise<Object>} Данные альбома с вложенными фотографиями
   *
   * @example
   * const album = await galleryService.getAlbum(1);
   */
  async getAlbum(id) {
    return api.get(`${BASE_URL}/albums/${id}/`);
  },

  /**
   * Получает список фотографий.
   *
   * @async
   * @param {Object} [params={}] - Параметры запроса
   * @param {string} [params.page] - Номер страницы
   * @param {string} [params.album] - Фильтр по ID альбома
   * @param {string} [params.tags__slug] - Фильтр по слагу тега
   * @return {Promise<Object>} Объект со списком фотографий
   *
   * @example
   * const photos = await galleryService.getPhotos();
   *
   * @example
   * // Получить фотографии из альбома
   * const photos = await galleryService.getPhotos({ album: 1 });
   */
  async getPhotos(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${BASE_URL}/photos/?${queryString}` : `${BASE_URL}/photos/`;
    return api.get(url);
  },

  /**
   * Получает детальную информацию о фотографии.
   *
   * @async
   * @param {number} id - ID фотографии
   * @return {Promise<Object>} Данные фотографии
   *
   * @example
   * const photo = await galleryService.getPhoto(1);
   */
  async getPhoto(id) {
    return api.get(`${BASE_URL}/photos/${id}/`);
  },

  /**
   * Загружает фотографии на сервер.
   *
   * @async
   * @param {number} albumId - ID альбома для загрузки
   * @param {File[]} files - Массив файлов для загрузки
   * @param {Function} [onProgress] - Callback для отслеживания прогресса
   * @return {Promise<Object[]>} Массив результатов загрузки
   *
   * @example
   * const results = await galleryService.uploadPhotos(1, [file1, file2]);
   */
  async uploadPhotos(albumId, files, onProgress) {
    const results = [];
    const uploadUrl = `${BASE_URL}/upload/upload/`;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('album_id', albumId);
      formData.append('photos', file);

      try {
        // Для FormData используем postForm метод API клиента
        const result = await api.postForm(uploadUrl, formData);
        results.push({ file: file.name, success: true, data: result });

        if (onProgress) {
          onProgress(file.name, { progress: 100, status: 'success' });
        }
      } catch (error) {
        results.push({ file: file.name, success: false, error: error.message });

        if (onProgress) {
          onProgress(file.name, { progress: 0, status: 'error', error: error.message });
        }
      }
    }

    return results;
  },

  /**
   * Получает список тегов.
   *
   * @async
   * @return {Promise<Object>} Объект со списком тегов
   *
   * @example
   * const tags = await galleryService.getTags();
   */
  async getTags() {
    return api.get(`${BASE_URL}/tags/`);
  },

  /**
   * Получает детальную информацию о теге.
   *
   * @async
   * @param {string} slug - Слаг тега
   * @return {Promise<Object>} Данные тега
   *
   * @example
   * const tag = await galleryService.getTag('nature');
   */
  async getTag(slug) {
    return api.get(`${BASE_URL}/tags/${slug}/`);
  },
};

export default galleryService;
