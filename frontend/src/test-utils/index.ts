/**
 * Фабрики тестовых данных API и вспомогательные стабы.
 *
 * Фабрики строят полные валидные объекты схем API с нейтральными
 * значениями по умолчанию; тест переопределяет через аргумент только
 * значимые для него поля. Дефолты подобраны так, чтобы не создавать
 * видимого содержимого: текстовые EXIF-поля пустые (компоненты фильтруют
 * пустые значения), счетчики нулевые, даты фиксированные.
 */

import type { components } from '@api-types/api-schema';
import type { Paginated } from '@api-types/pagination';

type AlbumDetail = components['schemas']['AlbumDetail'];
type AlbumList = components['schemas']['AlbumList'];
type Article = components['schemas']['Article'];
type Category = components['schemas']['Category'];
type Comment = components['schemas']['Comment'];
type Photo = components['schemas']['Photo'];
type PhotoDetail = components['schemas']['PhotoDetail'];
type Series = components['schemas']['Series'];
type Topic = components['schemas']['Topic'];

/** Фотография из списковых ответов API. */
export const makePhoto = (overrides: Partial<Photo> = {}): Photo => ({
  id: 1,
  tags: [],
  album_name: 'Альбом',
  thumbnail_url: '/media/photos/thumb.jpg',
  preview_url: '/media/photos/preview.jpg',
  image_url: '/media/photos/original.jpg',
  camera: '',
  lens_model: '',
  aperture: null,
  exposure: null,
  iso: null,
  focal_length: null,
  image: '/media/photos/original.jpg',
  uploaded_at: '',
  taken_at: '',
  modified_at: '',
  album: 1,
  exif: null,
  ...overrides,
});

/** Фотография из детального ответа API с идентификаторами соседей. */
export const makePhotoDetail = (overrides: Partial<PhotoDetail> = {}): PhotoDetail => ({
  id: 1,
  tags: [],
  album_name: 'Альбом',
  thumbnail_url: '/media/photos/thumb.jpg',
  preview_url: '/media/photos/preview.jpg',
  image_url: '/media/photos/original.jpg',
  camera: '',
  lens_model: '',
  aperture: null,
  exposure: null,
  iso: null,
  focal_length: null,
  previous_id: null,
  next_id: null,
  image: '/media/photos/original.jpg',
  uploaded_at: '',
  taken_at: '',
  modified_at: '',
  album: 1,
  exif: null,
  ...overrides,
});

/** Альбом из списковых ответов API. */
export const makeAlbum = (overrides: Partial<AlbumList> = {}): AlbumList => ({
  id: 1,
  tags: [],
  cover_thumbnail_url: '',
  photos_count: 0,
  name: 'Альбом',
  created_at: '',
  updated_at: '',
  ...overrides,
});

/** Альбом из детального ответа API со списком фотографий. */
export const makeAlbumDetail = (overrides: Partial<AlbumDetail> = {}): AlbumDetail => ({
  id: 1,
  tags: [],
  cover_thumbnail_url: '',
  photos: [],
  name: 'Альбом',
  created_at: '',
  updated_at: '',
  ...overrides,
});

/** Статья блога. */
export const makeArticle = (overrides: Partial<Article> = {}): Article => ({
  id: 1,
  author_username: 'author',
  categories: [],
  topics: [],
  series: [],
  comments: [],
  url: '/blog/article-1/',
  title: 'Статья',
  content: '',
  modified_at: '2026-01-01T00:00:00Z',
  ...overrides,
});

/** Комментарий к статье. */
export const makeComment = (overrides: Partial<Comment> = {}): Comment => ({
  id: 1,
  article: 1,
  author: 1,
  author_username: 'Автор',
  content: 'Комментарий',
  posted: '2026-01-01T00:00:00Z',
  ...overrides,
});

/** Категория блога. */
export const makeCategory = (overrides: Partial<Category> = {}): Category => ({
  id: 1,
  name: 'Категория',
  ...overrides,
});

/** Серия статей. */
export const makeSeries = (overrides: Partial<Series> = {}): Series => ({
  id: 1,
  name: 'Серия',
  ...overrides,
});

/** Тема статей. */
export const makeTopic = (overrides: Partial<Topic> = {}): Topic => ({
  id: 1,
  name: 'Тема',
  ...overrides,
});

/**
 * Собирает пагинированный конверт ответа API из списка результатов.
 * Необязательный аргумент extra переопределяет поля пагинации
 * (total_pages, next, previous).
 */
export const paginate = <T>(results: T[], extra: Partial<Paginated<T>> = {}): Paginated<T> => ({
  count: results.length,
  total_pages: 1,
  next: null,
  previous: null,
  results,
  ...extra,
});

/** Слушатель события смены системной темы. */
type ChangeListener = (event: MediaQueryListEvent) => void;

/** Управляемый стаб window.matchMedia. */
export interface MatchMediaStub {
  /** Функция для подстановки в window.matchMedia. */
  query: (query: string) => MediaQueryList;
  /** Эмулирует смену системной темы событием change. */
  triggerChange: (matches: boolean) => void;
}

/**
 * Создает управляемый стаб window.matchMedia: jsdom не реализует
 * этот API, а тестам темы нужен контроль совпадения запроса
 * prefers-color-scheme и эмуляция смены системной темы.
 */
export const createMatchMediaStub = (initialMatches: boolean): MatchMediaStub => {
  const listeners = new Set<ChangeListener>();
  const mediaQuery = {
    matches: initialMatches,
    addEventListener: jest.fn((event: string, listener: ChangeListener) => listeners.add(listener)),
    removeEventListener: jest.fn((event: string, listener: ChangeListener) => listeners.delete(listener)),
  };
  return {
    query: jest.fn((): MediaQueryList => mediaQuery as unknown as MediaQueryList),
    triggerChange: (matches: boolean) => {
      mediaQuery.matches = matches;
      listeners.forEach((listener) => listener({ matches } as MediaQueryListEvent));
    },
  };
};
