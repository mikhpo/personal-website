/**
 * Единые пользовательские сообщения списков.
 */

/**
 * Сообщение о пустом результате: при активном поиске включает запрос
 * пользователя, иначе возвращает базовое сообщение раздела.
 *
 * @example
 * searchEmptyMessage(search, 'Нет доступных фотографий');
 */
export function searchEmptyMessage(search: string | undefined, fallback: string): string {
  return search ? `По запросу "${search}" ничего не найдено` : fallback;
}
