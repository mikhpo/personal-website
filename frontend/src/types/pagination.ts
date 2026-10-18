/**
 * Конверт постраничного ответа REST API.
 *
 * Структурно повторяет сгенерированные схемы Paginated* из api-schema.ts:
 * конкретные конверты (PaginatedPhotoList, PaginatedArticleList и другие)
 * присваиваемы этому типу за счет структурной совместимости, а next и previous
 * необязательны ровно как в сгенерированной схеме.
 */
export interface Paginated<T> {
  count: number;
  /** @example 7 */
  total_pages: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}
