import { useState, useEffect, useCallback } from 'react';

/**
 * Хук для синхронизации состояния с localStorage.
 *
 * Позволяет сохранять и считывать состояние в/из localStorage браузера.
 * Поддерживает сериализацию JSON и автоматическую синхронизацию при изменениях.
 *
 * @param {string} key - Ключ для хранения в localStorage
 * @param {any} initialValue - Начальное значение (если в localStorage ничего нет)
 * @return {Array} Массив [value, setValue]
 * @property {any} value - Текущее значение из localStorage
 * @property {Function} setValue - Функция для обновления значения (с сохранением в localStorage)
 *
 * @example
 * // Хранение настроек
 * const [theme, setTheme] = useLocalStorage('theme', 'light');
 *
 * @example
 * // Хранение объектов
 * const [userPreferences, setUserPreferences] = useLocalStorage('prefs', {
 *   language: 'ru',
 *   fontSize: 14
 * });
 */
const useLocalStorage = (key, initialValue) => {
  /**
   * Функция для чтения значения из localStorage.
   * @return {any} Значение из localStorage или initialValue
   */
  const readValue = useCallback(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Ошибка чтения из localStorage ключа "${key}":`, error);
      return initialValue;
    }
  }, [initialValue, key]);

  const [storedValue, setStoredValue] = useState(readValue);

  /**
   * Функция для обновления значения.
   * Сохраняет новое значение в localStorage и обновляет состояние.
   * @function
   * @param {any} value - Новое значение
   * @return {void}
   */
  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Ошибка записи в localStorage ключа "${key}":`, error);
    }
  }, [key, storedValue]);

  useEffect(() => {
    const initializeValue = () => {
      const updateValueState = () => {
        setStoredValue(readValue());
      };
      updateValueState();
    };
    initializeValue();
  }, [readValue]);

  return [storedValue, setValue];
};

export default useLocalStorage;
