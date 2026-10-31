/**
 * Утилиты работы с HTML-строками.
 */

/** Удаляет HTML-теги и пробелы по краям. */
export function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '').trim();
}

/**
 * Считает слова в сыром HTML: слово - любая группа символов между пробельными
 * символами, включая содержимое тегов и их атрибуты.
 */
export function countHtmlWords(html: string): number {
  return html.split(/\s+/).filter(Boolean).length;
}

/** Void-элементы HTML: закрываются неявно и не попадают на стек открытых тегов. */
const VOID_ELEMENTS = new Set([
  'area',
  'base',
  'br',
  'col',
  'embed',
  'hr',
  'img',
  'input',
  'link',
  'meta',
  'param',
  'source',
  'track',
  'wbr',
]);

/**
 * Разбивает текстовый узел на слова с ведущим пробелом узла.
 *
 * Пробельные последовательности внутри узла схлопываются; ведущий пробел
 * сохраняется отдельно, чтобы при обрезке узла начать с него. Пробельный
 * узел дает одно слово.
 */
function splitNodeWords(node: string): { leading: string; words: string[] } {
  const leading = node.match(/^\s*/)?.[0] ?? '';
  const trailing = node.match(/\s*$/)?.[0] ?? '';
  const core = node.slice(leading.length, node.length - trailing.length);
  return { leading, words: core ? core.split(/\s+/) : [node] };
}

/**
 * Обрезает HTML до указанного числа слов, не ломая разметку.
 *
 * Слова считаются только в текстовых узлах, теги словами не являются; при
 * обрезке к последнему узлу добавляется многоточие, а открытые к этому
 * моменту теги закрываются в обратном порядке. Void-элементы (img, br и т.п.)
 * на стек не попадают и сохраняются, если встретились до точки обрезки.
 * Комментарии и doctype выпадают из результата. HTML короче лимита
 * возвращается без изменений.
 *
 * Разметка разбирается по тегам регулярным выражением, поэтому `>` внутри
 * значений атрибутов не поддерживается - редактор TinyMCE такую разметку
 * не создает.
 */
export function truncateHtmlWords(html: string, maxWords: number): string {
  if (maxWords <= 0) {
    return '';
  }

  const parts: string[] = [];
  const openTags: string[] = [];
  let remaining = maxWords;
  let truncated = false;

  for (const part of html.split(/(<[^>]*>)/)) {
    if (!part) {
      continue;
    }
    if (!part.startsWith('<')) {
      const { leading, words } = splitNodeWords(part);
      if (words.length > remaining) {
        const sliced = words.slice(0, remaining);
        // Ведущий пробел принадлежит первому слову среза: при пустом срезе
        // многоточие следует сразу за предыдущим узлом
        parts.push((sliced.length ? leading : '') + sliced.join(' '), '\u2026');
        truncated = true;
        break;
      }
      remaining -= words.length;
      parts.push(part);
      continue;
    }

    if (part.startsWith('<!')) {
      continue;
    }

    const tagMatch = part.match(/^<\/?([a-zA-Z][a-zA-Z0-9-]*)/);
    if (!tagMatch) {
      parts.push(part);
      continue;
    }
    const tag = (tagMatch[1] ?? '').toLowerCase();
    const isVoid = VOID_ELEMENTS.has(tag);
    parts.push(part);
    if (part[1] === '/') {
      if (!isVoid && openTags[openTags.length - 1] === tag) {
        openTags.pop();
      }
    } else if (!isVoid && !/\/\s*>$/.test(part)) {
      openTags.push(tag);
    }
  }

  if (!truncated) {
    return html;
  }
  for (const tag of openTags.reverse()) {
    parts.push(`</${tag}>`);
  }
  return parts.join('');
}
