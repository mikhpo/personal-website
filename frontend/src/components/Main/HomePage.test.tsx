/**
 * Тесты для компонента HomePage.
 *
 * Проверяет корректность отображения главной страницы с категориями и сериями.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import HomePage from '@components/Main/HomePage';

// Мокировать компонент CardGrid для изоляции тестов
jest.mock('@components/Main/CardGrid', () => {
  const MockCardGrid = ({ testId }: { testId: string }) => <div data-testid={testId}>CardGrid</div>;
  MockCardGrid.displayName = 'CardGrid';
  return {
    __esModule: true,
    default: MockCardGrid,
  };
});

describe('HomePage', () => {
  /**
   * Проверяет, что компонент корректно рендерится.
   * Должны отображаться две сетки справочников с прежними testid.
   */
  test('рендерит сетки категорий и серий', () => {
    render(<HomePage />);

    expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
    expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
  });
});
