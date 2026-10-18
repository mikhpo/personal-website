import { useCallback, useState } from 'react';

/** Результат хока useToggle: [value, toggle, setTrue, setFalse]. */
export type UseToggleResult = readonly [boolean, () => void, () => void, () => void];

/**
 * Хук для управления булевым состоянием с функциями переключения.
 *
 * Упрощает работу с булевыми состояниями, предоставляя удобные функции
 * для переключения, включения и выключения.
 *
 * @example
 * const [isOpen, toggle, open, close] = useToggle(false);
 */
const useToggle = (initialValue = false): UseToggleResult => {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue((v) => !v);
  }, []);

  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return [value, toggle, setTrue, setFalse] as const;
};

export default useToggle;
