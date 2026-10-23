/**
 * Утилиты для построения URL API-запросов.
 *
 * Централизует сборку URL фильтрации во фронтенде: фильтры передаются как
 * структурированные данные (объект параметров), а итоговый URL формируется здесь.
 */

/** Значения параметров запроса; пустые пропускаются при сборке URL. */
export type QueryParamValue = string | number | boolean | null | undefined;

/**
 * Собирает URL запроса из базового URL и объекта параметров.
 *
 * Пустые значения (undefined, null, "") пропускаются, чтобы активные фильтры
 * можно было передавать единообразно, не очищая их заранее. Возвращается
 * относительный URL (pathname + search), пригодный для same-origin fetch.
 *
 * @example
 * buildApiUrl("/api/gallery/albums/", { tags__slug: "example-tag", page: 1 })
 * // "/api/gallery/albums/?tags__slug=example-tag&page=1"
 *
 * @example
 * buildApiUrl("/api/gallery/albums/?ordering=name", { page: 2 })
 * // "/api/gallery/albums/?ordering=name&page=2"
 */
export function buildApiUrl(base: string, params: Record<string, QueryParamValue> = {}): string {
  const url = new URL(base, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.append(key, String(value));
    }
  });
  return url.pathname + url.search;
}
