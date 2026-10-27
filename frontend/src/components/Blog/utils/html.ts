/**
 * Утилиты работы с HTML-строками.
 */

/** Удаляет HTML-теги и пробелы по краям. */
export function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '').trim();
}
