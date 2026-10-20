/**
 * Сервис для работы с API галереи.
 *
 * Предоставляет методы для выполнения запросов к API галереи:
 * - Получение списка альбомов и фотографий
 * - Загрузка фотографий
 * - Работа с тегами
 *
 * Типы ответов и параметров берутся из сгенерированной OpenAPI-схемы;
 * списочные методы возвращают конверт пагинации.
 */

import type { components, operations } from '../types/api-schema';
import type { Paginated } from '../types/pagination';
import api from './api';
import { buildApiUrl } from '../utils/apiUrl';

type AlbumList = components['schemas']['AlbumList'];
type AlbumDetail = components['schemas']['AlbumDetail'];
type Photo = components['schemas']['Photo'];
type PhotoDetail = components['schemas']['PhotoDetail'];
type Tag = components['schemas']['Tag'];
type UploadResponse = components['schemas']['UploadResponse'];

type AlbumListQuery = operations['gallery_albums_list']['parameters']['query'];
type PhotoListQuery = operations['gallery_photos_list']['parameters']['query'];

/** Прогресс загрузки одного файла для колбэка onProgress. */
export interface UploadProgressState {
  progress: number;
  /** Состояния колбэка; сам сервис по завершении файла шлет только success и error */
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

/** Результат загрузки одного файла. */
export interface UploadOutcome {
  file: string;
  success: boolean;
  data?: UploadResponse;
  error?: string;
}

const BASE_URL = '/api/gallery';

export const galleryService = {
  /**
   * Получает список альбомов.
   *
   * @example
   * const albums = await galleryService.getAlbums();
   */
  async getAlbums(params: AlbumListQuery = {}): Promise<Paginated<AlbumList>> {
    return api.get(buildApiUrl(`${BASE_URL}/albums/`, params));
  },

  /**
   * Получает детальную информацию об альбоме.
   *
   * @example
   * const album = await galleryService.getAlbum(1);
   */
  async getAlbum(id: number | string): Promise<AlbumDetail> {
    return api.get(`${BASE_URL}/albums/${id}/`);
  },

  /**
   * Получает список фотографий.
   *
   * @example
   * const photos = await galleryService.getPhotos();
   *
   * @example
   * const photos = await galleryService.getPhotos({ album: 1 });
   */
  async getPhotos(params: PhotoListQuery = {}): Promise<Paginated<Photo>> {
    return api.get(buildApiUrl(`${BASE_URL}/photos/`, params));
  },

  /**
   * Получает детальную информацию о фотографии.
   *
   * @example
   * const photo = await galleryService.getPhoto(1);
   */
  async getPhoto(id: number | string): Promise<PhotoDetail> {
    return api.get(`${BASE_URL}/photos/${id}/`);
  },

  /**
   * Загружает фотографии на сервер.
   *
   * @example
   * const results = await galleryService.uploadPhotos(1, [file1, file2]);
   */
  async uploadPhotos(
    albumId: number,
    files: File[],
    onProgress?: (fileName: string, state: UploadProgressState) => void,
  ): Promise<UploadOutcome[]> {
    const results: UploadOutcome[] = [];
    const uploadUrl = `${BASE_URL}/upload/`;

    for (const file of files) {
      const formData = new FormData();
      formData.append('album_id', String(albumId));
      formData.append('photos', file);

      try {
        // Для FormData используем postForm метод API клиента
        const result = await api.postForm<UploadResponse>(uploadUrl, formData);
        results.push({ file: file.name, success: true, data: result });

        if (onProgress) {
          onProgress(file.name, { progress: 100, status: 'success' });
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        results.push({ file: file.name, success: false, error: message });

        if (onProgress) {
          onProgress(file.name, { progress: 0, status: 'error', error: message });
        }
      }
    }

    return results;
  },

  /**
   * Получает список тегов.
   *
   * @example
   * const tags = await galleryService.getTags();
   */
  async getTags(): Promise<Paginated<Tag>> {
    return api.get(`${BASE_URL}/tags/`);
  },

  /**
   * Получает детальную информацию о теге.
   *
   * @example
   * const tag = await galleryService.getTag('nature');
   */
  async getTag(slug: string): Promise<Tag> {
    return api.get(`${BASE_URL}/tags/${slug}/`);
  },
};

export default galleryService;
