/**
 * Экспорт всех хуков.
 *
 * Централизованный экспорт для удобного импорта в компонентах.
 *
 * @example
 * import { useApiData, usePagination } from '@hooks';
 */

// Общие хуки
export { default as useApiData } from './useApiData';
export { default as usePagination } from './usePagination';
export { default as useToggle } from './useToggle';
export { default as useLocalStorage } from './useLocalStorage';

// Специализированные хуки галереи
export { default as usePhotoData } from './usePhotoData';
export { default as useAlbumPhotos } from './useAlbumPhotos';
export { default as usePhotoNavigation } from './usePhotoNavigation';
