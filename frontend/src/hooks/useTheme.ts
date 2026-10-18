import { useCallback, useEffect, useState } from 'react';
import useLocalStorage from './useLocalStorage';

/** Действующая тема сайта (Bootstrap color modes). */
export type ThemeName = 'light' | 'dark';

const STORAGE_KEY = 'theme';
const LIGHT_THEME: ThemeName = 'light';
const DARK_THEME: ThemeName = 'dark';
const MEDIA_QUERY = '(prefers-color-scheme: dark)';

/** Результат хока useTheme. */
export interface UseThemeResult {
  /** Действующая тема. */
  theme: ThemeName;
  /** Системная тема браузера. */
  systemTheme: ThemeName;
  /** Явный выбор пользователя: 'light', 'dark' или null (следовать системе). */
  storedTheme: string | null;
  /** Устанавливает тему: 'light', 'dark' или null для возврата к системной. */
  setTheme: (value: ThemeName | null) => void;
  /** Переключает между 'light' и 'dark' (записывает явный выбор). */
  toggleTheme: () => void;
}

/**
 * Возвращает системную тему браузера.
 * Если системную тему определить нельзя (нет matchMedia), используется светлая.
 */
const getSystemTheme = (): ThemeName => {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return LIGHT_THEME;
  }
  return window.matchMedia(MEDIA_QUERY).matches ? DARK_THEME : LIGHT_THEME;
};

/**
 * Хук для управления темой сайта (Bootstrap color modes).
 *
 * Приоритет темы: явный выбор пользователя в localStorage под ключом 'theme',
 * затем системная тема (prefers-color-scheme), затем светлая.
 * Выбранная тема синхронизируется с атрибутом data-bs-theme на элементе <html>,
 * смена системной темы ОС отслеживается на лету, пока пользователь не сделал явный выбор.
 *
 * @example
 * const { theme, toggleTheme } = useTheme();
 *
 * @example
 * const { theme, setTheme } = useTheme();
 * setTheme('dark');
 * setTheme(null); // снова следовать системной теме
 */
const useTheme = (): UseThemeResult => {
  const [storedTheme, setStoredTheme] = useLocalStorage<string>(STORAGE_KEY, null);
  const [systemTheme, setSystemTheme] = useState<ThemeName>(getSystemTheme);

  // Отслеживание смены системной темы: действует до явного выбора пользователя
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return undefined;
    }
    const mediaQuery = window.matchMedia(MEDIA_QUERY);
    const handleChange = (event: MediaQueryListEvent) => {
      setSystemTheme(event.matches ? DARK_THEME : LIGHT_THEME);
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Явный выбор учитывается только для валидных значений:
  // мусор в localStorage обрабатывается так же, как его отсутствие
  const theme: ThemeName = storedTheme === LIGHT_THEME || storedTheme === DARK_THEME ? storedTheme : systemTheme;

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-bs-theme', theme);
    }
  }, [theme]);

  const setTheme = useCallback(
    (value: ThemeName | null) => {
      setStoredTheme(value === LIGHT_THEME || value === DARK_THEME ? value : null);
    },
    [setStoredTheme],
  );

  const toggleTheme = useCallback(() => {
    setTheme(theme === DARK_THEME ? LIGHT_THEME : DARK_THEME);
  }, [setTheme, theme]);

  return { theme, systemTheme, storedTheme, setTheme, toggleTheme };
};

export default useTheme;
