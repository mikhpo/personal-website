import React from 'react';
import { render, screen } from '@testing-library/react';
import NumbersPagination from './NumbersPagination';

/**
 * Тесты для компонента NumbersPagination
 */
describe('NumbersPagination', () => {
  test('рендерит номера страниц', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  test('рендерит многоточия при большом количестве страниц', () => {
    render(<NumbersPagination currentPage={5} totalPages={20} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
  });

  test('активная страница не является ссылкой', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const activePage = screen.getByText('3').closest('a');
    expect(activePage).toBeNull();
  });

  test('неактивные страницы являются ссылками', () => {
    render(<NumbersPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const inactivePage = screen.getByText('1').closest('a');
    expect(inactivePage).toHaveAttribute('href', '/blog/?page=1');
  });

  test('рендерит первую и последнюю страницы с многоточиями', () => {
    render(<NumbersPagination currentPage={10} totalPages={20} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
  });
});
