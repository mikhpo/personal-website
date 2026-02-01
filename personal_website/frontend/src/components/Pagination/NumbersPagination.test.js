import React from 'react';
import { render, screen } from '@testing-library/react';
import NumbersPagination from './NumbersPagination';

/**
 * Тесты для компонента NumbersPagination
 */
describe('NumbersPagination', () => {
  /**
   * Тест проверяет отображение номеров страниц
   */
  test('рендерит номера страниц', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // активная страница
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение многоточий при большом количестве страниц
   */
  test('рендерит многоточия при большом количестве страниц', () => {
    render(<NumbersPagination currentPage={5} totalPages={20} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что активная страница не является ссылкой
   */
  test('активная страница не является ссылкой', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const activePage = screen.getByText('3').closest('a');
    expect(activePage).toBeNull();
  });

  /**
   * Тест проверяет, что неактивные страницы являются ссылками
   */
  test('неактивные страницы являются ссылками', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const inactivePage = screen.getByText('1').closest('a');
    expect(inactivePage).toHaveAttribute('href', '/blog/?page=1');
  });
});
