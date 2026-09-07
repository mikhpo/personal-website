import { useState, useEffect, useCallback } from 'react';
import useLocalStorage from './useLocalStorage';

const STORAGE_KEY = 'theme';
const LIGHT_THEME = 'light';
const DARK_THEME = 'dark';
const MEDIA_QUERY = '(prefers-color-scheme: dark)';

/**
 * Возвращает системную тему браузера.
 * Если системную тему определить нельзя (нет matchMedia), используется светлая.
 * @return {string} 'dark' или 'light'
 */
const getSystemTheme = () => {
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
 * @return {Object} Объект с состоянием и функциями управления темой
 * @property {string} theme - Действующая тема: 'light' или 'dark'
 * @property {string} systemTheme - Системная тема браузера: 'light' или 'dark'
 * @property {(string|null)} storedTheme - Явный выбор пользователя: 'light', 'dark' или null (следовать системе)
 * @property {Function} setTheme - Устанавливает тему: 'light', 'dark' или null для возврата к системной
 * @property {Function} toggleTheme - Переключает между 'light' и 'dark' (записывает явный выбор)
 *
 * @example
 * // Отображение и переключение темы
 * const { theme, toggleTheme } = useTheme();
 *
 * @example
 * // Выбор конкретной темы с возможностью вернуть системную
 * const { theme, setTheme } = useTheme();
 * setTheme('dark');
 * setTheme(null); // снова следовать системной теме
 */
const useTheme = () => {
  const [storedTheme, setStoredTheme] = useLocalStorage(STORAGE_KEY, null);
  const [systemTheme, setSystemTheme] = useState(getSystemTheme);

  // Отслеживание смены системной темы: действует до явного выбора пользователя
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return undefined;
    }
    const mediaQuery = window.matchMedia(MEDIA_QUERY);
    const handleChange = (event) => {
      setSystemTheme(event.matches ? DARK_THEME : LIGHT_THEME);
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Явный выбор учитывается только для валидных значений:
  // мусор в localStorage обрабатывается так же, как его отсутствие
  const theme = storedTheme === LIGHT_THEME || storedTheme === DARK_THEME ? storedTheme : systemTheme;

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-bs-theme', theme);
    }
  }, [theme]);

  const setTheme = useCallback(
    (value) => {
      setStoredTheme(value === LIGHT_THEME || value === DARK_THEME ? value : null);
    },
    [setStoredTheme]
  );

  const toggleTheme = useCallback(() => {
    setTheme(theme === DARK_THEME ? LIGHT_THEME : DARK_THEME);
  }, [setTheme, theme]);

  return { theme, systemTheme, storedTheme, setTheme, toggleTheme };
};

export default useTheme;
