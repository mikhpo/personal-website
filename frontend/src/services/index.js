/**
 * Экспорт всех сервисов API.
 *
 * Централизованный экспорт для удобного импорта в компонентах.
 *
 * @example
 * import { blogService, galleryService, api } from '@services';
 */

export { blogService } from './blogService';
export { galleryService } from './galleryService';
export { default as api, ApiError } from './api';
