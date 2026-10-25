import { useEffect, useState } from 'react';
import type { ThemeName } from './useTheme';

export const THEME_ATTRIBUTE = 'data-bs-theme';
const FALLBACK_THEME: ThemeName = 'light';

/** Читает действующую тему из атрибута на элементе <html>; не-'dark' читается как светлая. */
const readHtmlTheme = (): ThemeName => {
  const value = document.documentElement.getAttribute(THEME_ATTRIBUTE);
  return value === 'dark' ? 'dark' : 'light';
};

/**
 * Хук для чтения действующей темы сайта из атрибута data-bs-theme на элементе <html>.
 *
 * В отличие от useTheme (владелец состояния и записи атрибута), хук только
 * читает атрибут и следит за его изменениями через MutationObserver, поэтому
 * реагирует на переключение темы из любого места страницы, например из
 * переключателя в навигационной панели.
 *
 * @example
 * const theme = useHtmlTheme();
 * const isDark = theme === 'dark';
 */
const useHtmlTheme = (): ThemeName => {
  const [theme, setTheme] = useState<ThemeName>(() => {
    if (typeof document === 'undefined') {
      return FALLBACK_THEME;
    }
    return readHtmlTheme();
  });

  useEffect(() => {
    if (typeof document === 'undefined' || typeof MutationObserver === 'undefined') {
      return undefined;
    }
    const observer = new MutationObserver(() => {
      setTheme(readHtmlTheme());
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
