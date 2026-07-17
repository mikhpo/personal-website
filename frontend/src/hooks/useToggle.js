import { useState, useCallback } from 'react';

/**
 * Хук для управления булевым состоянием с функциями переключения.
 *
 * Упрощает работу с булевыми состояниями, предоставляя удобные функции
 * для переключения, включения и выключения.
 *
 * @param {boolean} [initialValue=false] - Начальное значение
 * @return {Array} Массив [value, toggle, setTrue, setFalse]
 * @property {boolean} value - Текущее значение
 * @property {Function} toggle - Функция для переключения значения
 * @property {Function} setTrue - Функция для установки значения в true
 * @property {Function} setFalse - Функция для установки значения в false
 *
 * @example
 * // Базовое использование
 * const [isOpen, toggle, setIsOpen, close] = useToggle(false);
 *
 * @example
 * // Использование с модальным окном
 * const [isModalOpen, toggleModal, openModal, closeModal] = useToggle(false);
 */
const useToggle = (initialValue = false) => {
  const [value, setValue] = useState(initialValue);

  /**
   * Переключает значение на противоположное.
   * @function
   * @return {void}
   */
  const toggle = useCallback(() => {
    setValue(v => !v);
  }, []);

  /**
   * Устанавливает значение в true.
   * @function
   * @return {void}
   */
  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  /**
   * Устанавливает значение в false.
   * @function
   * @return {void}
   */
  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return [value, toggle, setTrue, setFalse];
};

export default useToggle;
