/**
 * Единый разбор списочных ответов REST API.
 *
 * Списочные эндпоинты отдают пагинированный ответ; единственный готовый массив
 * возвращает детальный эндпоинт альбома (поле photos). Функция сводит обе
 * реальные формы к одному виду, который потребляют компоненты.
 */

import type { Paginated } from '@api-types/pagination';

/** Результат разбора списочного ответа. */
export interface ParsedList<T> {
  items: T[];
  count: number;
  /** Число страниц из ответа пагинации; для готового массива - одна страница. */
  totalPages: number;
  next: string | null;
  previous: string | null;
}

/**
 * Разбирает списочный ответ API: пагинированный ответ или готовый массив.
 *
 * @example
 * const { items, count, totalPages } = parseListResponse(await galleryService.getPhotos());
 */
export function parseListResponse<T>(data: Paginated<T> | T[]): ParsedList<T> {
  if (Array.isArray(data)) {
    return { items: data, count: data.length, totalPages: 1, next: null, previous: null };
  }
  return {
    items: data.results,
    count: data.count,
    totalPages: data.total_pages,
    next: data.next ?? null,
    previous: data.previous ?? null,
  };
}
