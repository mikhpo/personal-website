/* eslint-disable react-x/set-state-in-effect -- чтение хранилища в effect перечитывает значение при смене key/initialValue; без синхронизации перестройка меняла бы рантайм */
import { useCallback, useEffect, useState, type SetStateAction } from 'react';

/**
 * Хук для синхронизации состояния с localStorage.
 *
 * Позволяет сохранять и считывать состояние в/из localStorage браузера.
 * Поддерживает сериализацию JSON; при смене key или initialValue значение
 * перечитывается из хранилища. Межвкладочная синхронизация не выполняется:
 * изменение хранилища в другой вкладке не отражается в открытых вкладках.
 * Запись null или undefined удаляет ключ из localStorage.
 *
 * @example
 * const [theme, setTheme] = useLocalStorage<string>('theme', 'light');
 *
 * @example
 * const [preferences, setPreferences] = useLocalStorage('prefs', { language: 'ru', fontSize: 14 });
 */
const useLocalStorage = <T>(key: string, initialValue: T | null) => {
  /** Читает значение из localStorage; при отсутствии или ошибке - начальное. */
  const readValue = useCallback((): T | null => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch (error) {
      console.warn(`Ошибка чтения из localStorage ключа "${key}":`, error);
      return initialValue;
    }
  }, [initialValue, key]);

  const [storedValue, setStoredValue] = useState<T | null | undefined>(readValue);

  /**
   * Сохраняет значение в localStorage и обновляет состояние; null и undefined
   * удаляют ключ, а состояние принимает переданное значение как есть.
   *
   * Приведение при сужении необходимо: T не ограничен и сам может быть функцией,
   * поэтому typeof-проверка не сужает тип до обновляющей функции.
   */
  const setValue = useCallback(
    (value: SetStateAction<T | null | undefined>) => {
      try {
        const valueToStore =
          typeof value === 'function'
            ? (value as (prev: T | null | undefined) => T | null | undefined)(storedValue)
            : value;
        setStoredValue(valueToStore);

        if (typeof window !== 'undefined') {
          if (valueToStore === null || valueToStore === undefined) {
            window.localStorage.removeItem(key);
          } else {
            window.localStorage.setItem(key, JSON.stringify(valueToStore));
          }
        }
      } catch (error) {
        console.warn(`Ошибка записи в localStorage ключа "${key}":`, error);
      }
    },
    [key, storedValue],
  );

  useEffect(() => {
    setStoredValue(readValue());
  }, [readValue]);

  return [storedValue, setValue] as const;
};

export default useLocalStorage;
