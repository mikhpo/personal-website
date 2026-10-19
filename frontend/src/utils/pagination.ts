/**
 * Единый разбор списочных ответов REST API.
 *
 * Списочные эндпоинты отдают конверт пагинации; единственный готовый массив
 * возвращает детальный эндпоинт альбома (поле photos). Функция сводит обе
 * реальные формы к одному виду, который потребляют компоненты.
 */

import type { Paginated } from '../types/pagination';

/** Результат разбора списочного ответа. */
export interface ParsedList<T> {
  items: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

/**
 * Разбирает списочный ответ API: конверт пагинации или готовый массив.
 *
 * @example
 * const { items, count, next } = parseListResponse(await galleryService.getPhotos());
 */
export function parseListResponse<T>(data: Paginated<T> | T[]): ParsedList<T> {
  if (Array.isArray(data)) {
    return { items: data, count: data.length, next: null, previous: null };
  }
  return {
    items: data.results,
    count: data.count,
    next: data.next ?? null,
    previous: data.previous ?? null,
  };
}
