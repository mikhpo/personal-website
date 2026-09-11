/**
 * Тесты для хука useHtmlTheme.
 *
 * Проверяет чтение действующей темы из атрибута data-bs-theme
 * на элементе <html> и реакцию на ее смену.
 */

import { renderHook, act } from '@testing-library/react';
import useHtmlTheme from './useHtmlTheme';

describe('useHtmlTheme', () => {
  /**
   * Проверяет чтение текущей темы из атрибута на старте.
   */
  test('возвращает тему из атрибута data-bs-theme', () => {
    document.documentElement.setAttribute('data-bs-theme', 'dark');
    const { result } = renderHook(() => useHtmlTheme());
    expect(result.current).toBe('dark');
  });

  /**
   * Проверяет значение по умолчанию при отсутствии атрибута.
   */
  test('возвращает светлую тему без атрибута', () => {
    document.documentElement.removeAttribute('data-bs-theme');
    const { result } = renderHook(() => useHtmlTheme());
    expect(result.current).toBe('light');
  });

  /**
   * Проверяет реакцию на смену атрибута после монтирования.
   */
  test('обновляется при смене темы', async () => {
    document.documentElement.setAttribute('data-bs-theme', 'light');
    const { result } = renderHook(() => useHtmlTheme());
    expect(result.current).toBe('light');

    // Уведомления MutationObserver доставляются асинхронно
    await act(async () => {
      document.documentElement.setAttribute('data-bs-theme', 'dark');
    });
    expect(result.current).toBe('dark');
  });
});
