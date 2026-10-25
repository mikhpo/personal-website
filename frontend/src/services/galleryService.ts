/**
 * Сервис для работы с API галереи.
 *
 * Предоставляет методы для выполнения запросов к API галереи:
 * - Получение списка альбомов и фотографий
 * - Загрузка фотографий
 * - Работа с тегами
 *
 * Типы ответов и параметров берутся из сгенерированной OpenAPI-схемы;
 * списочные методы возвращают пагинированный ответ.
 */

import type { components, operations } from '@api-types/api-schema';
import type { Paginated } from '@api-types/pagination';
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
  async getAlbum(id: number): Promise<AlbumDetail> {
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
  async getPhoto(id: number): Promise<PhotoDetail> {
    return api.get(`${BASE_URL}/photos/${id}/`);
  },

  /**
   * Загружает одну фотографию в альбом (multipart).
   *
   * @example
   * const response = await galleryService.uploadPhoto(1, file);
   */
  async uploadPhoto(albumId: number, file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('album_id', String(albumId));
    formData.append('photos', file);

    // Для FormData используем postForm метод API клиента
    return api.postForm<UploadResponse>(`${BASE_URL}/upload/`, formData);
  },

  /**
   * Получает полный список тегов: эндпоинт отдает все теги одной выдачей
   * без пагинации.
   *
   * @example
   * const tags = await galleryService.getTags();
   */
  async getTags(): Promise<Tag[]> {
    return api.get(`${BASE_URL}/tags/`);
  },
};

export default galleryService;
