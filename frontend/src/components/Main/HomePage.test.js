/**
 * Тесты для компонента HomePage.
 *
 * Проверяет корректность отображения главной страницы с категориями и сериями.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import HomePage from '@components/Main/HomePage';

// Мокировать компоненты CategoryGrid и SeriesGrid для изоляции тестов
jest.mock('@components/Main/CategoryGrid', () => {
  const MockCategoryGrid = () => <div data-testid="category-grid-mock">CategoryGrid</div>;
  MockCategoryGrid.displayName = 'CategoryGrid';
  return {
    __esModule: true,
    default: MockCategoryGrid,
  };
});

jest.mock('@components/Main/SeriesGrid', () => {
  const MockSeriesGrid = () => <div data-testid="series-grid-mock">SeriesGrid</div>;
  MockSeriesGrid.displayName = 'SeriesGrid';
  return {
    __esModule: true,
    default: MockSeriesGrid,
  };
});

describe('HomePage', () => {
  /**
   * Проверяет, что компонент корректно рендерится.
   * Должны отображаться CategoryGrid и SeriesGrid.
   */
  test('рендерит CategoryGrid и SeriesGrid', () => {
    render(<HomePage />);

    expect(screen.getByTestId('category-grid-mock')).toBeInTheDocument();
    expect(screen.getByTestId('series-grid-mock')).toBeInTheDocument();
  });
});
