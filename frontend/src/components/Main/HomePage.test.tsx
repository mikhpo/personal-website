/**
 * Тесты для компонента HomePage.
 *
 * Проверяет корректность отображения главной страницы с категориями и сериями.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import HomePage from '@components/Main/HomePage';

// Мокировать компонент TaxonomyGrid для изоляции тестов
jest.mock('@components/Main/TaxonomyGrid', () => {
  const MockTaxonomyGrid = ({ testId }: { testId: string }) => <div data-testid={testId}>TaxonomyGrid</div>;
  MockTaxonomyGrid.displayName = 'TaxonomyGrid';
  return {
    __esModule: true,
    default: MockTaxonomyGrid,
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
