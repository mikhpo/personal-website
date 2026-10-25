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

/**
 * Загружает список целиком, проходя все страницы пагинации.
 *
 * @example
 * const categories = await fetchAllPages(blogService.getCategories);
 */
export async function fetchAllPages<T>(fetchPage: (params: { page: number }) => Promise<Paginated<T>>): Promise<T[]> {
  const items: T[] = [];
  // Ограничение итераций защищает от зацикливания при некорректном API
  for (let page = 1; page <= 100; page += 1) {
    const { items: pageItems, next } = parseListResponse(await fetchPage({ page }));
    items.push(...pageItems);
    if (!next) {
      return items;
    }
  }
  return items;
}
