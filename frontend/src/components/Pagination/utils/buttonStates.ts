/** Тип навигационной кнопки пагинации. */
export type NavigationButtonType = 'first' | 'prev' | 'next' | 'last';

/**
 * Проверяет, должна ли кнопка быть отключена.
 */
export const isButtonDisabled = (type: NavigationButtonType, currentPage: number, totalPages: number): boolean => {
  switch (type) {
    case 'first':
    case 'prev':
      return currentPage === 1;
    case 'next':
    case 'last':
      return currentPage === totalPages;
    default:
      return false;
  }
};

/**
 * Получает URL для кнопки навигции; undefined, если кнопка отключена.
 */
export const getButtonHref = (
  type: NavigationButtonType,
  currentPage: number,
  totalPages: number,
  baseUrl: string,
): string | undefined => {
  if (isButtonDisabled(type, currentPage, totalPages)) {
    return undefined;
  }

  const separator = baseUrl.includes('?') ? '&' : '?';
  switch (type) {
    case 'first':
      return `${baseUrl}${separator}page=1`;
    case 'prev':
      return `${baseUrl}${separator}page=${currentPage - 1}`;
    case 'next':
      return `${baseUrl}${separator}page=${currentPage + 1}`;
    case 'last':
      return `${baseUrl}${separator}page=${totalPages}`;
    default:
      return undefined;
  }
};

/** Текст навигационной кнопки. */
const BUTTON_TEXT: Record<NavigationButtonType, string> = {
  first: 'первая',
  prev: 'предыдущая',
  next: 'следующая',
  last: 'последняя',
};

/**
 * Получает текст для кнопки навигации.
 */
export const getButtonText = (type: NavigationButtonType): string => BUTTON_TEXT[type] ?? '';

/**
 * Получает CSS-классы для кнопки навигации.
 */
export const getButtonClassName = (type: NavigationButtonType): string => {
  const baseClasses = 'btn btn-outline-dark';

  switch (type) {
    case 'first':
    case 'prev':
      return `${baseClasses} me-1`;
    case 'next':
    case 'last':
      return `${baseClasses} ms-1`;
    default:
      return baseClasses;
  }
};
