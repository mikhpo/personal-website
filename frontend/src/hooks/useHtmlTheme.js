import { useEffect, useState } from 'react';

const THEME_ATTRIBUTE = 'data-bs-theme';

/**
 * Возвращает действующую тему сайта из атрибута data-bs-theme на элементе <html>.
 *
 * В отличие от useTheme (владелец состояния и записи атрибута), хук только
 * читает атрибут и следит за его изменениями через MutationObserver, поэтому
 * реагирует на переключение темы из любого места страницы, например из
 * переключателя в навигационной панели.
 *
 * @return {string} Действующая тема: 'light' или 'dark'
 *
 * @example
 * // Перекрасить компонент при смене темы
 * const theme = useHtmlTheme();
 * const isDark = theme === 'dark';
 */
const useHtmlTheme = () => {
  const [theme, setTheme] = useState(() => {
    if (typeof document === 'undefined') {
      return 'light';
    }
    return document.documentElement.getAttribute(THEME_ATTRIBUTE) || 'light';
  });

  useEffect(() => {
    if (typeof document === 'undefined' || typeof MutationObserver === 'undefined') {
      return undefined;
    }
    const observer = new MutationObserver(() => {
      setTheme(document.documentElement.getAttribute(THEME_ATTRIBUTE) || 'light');
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: [THEME_ATTRIBUTE],
    });
    return () => observer.disconnect();
  }, []);

  return theme;
};

export default useHtmlTheme;
