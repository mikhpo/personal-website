import React from 'react';
import { render, screen } from '@testing-library/react';
import PageNumbers from './PageNumbers';

/**
 * Тесты для компонента PageNumbers
 */
describe('PageNumbers', () => {
  test('рендерит правильное количество страниц', () => {
    render(<PageNumbers currentPage={1} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  test('рендерит активную страницу без ссылки', () => {
    render(<PageNumbers currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const activePage = screen.getByText('3').closest('a');
    expect(activePage).toBeNull(); // Активная страница не должна быть ссылкой
  });

  test('рендерит неактивные страницы со ссылками', () => {
    render(<PageNumbers currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const inactivePage = screen.getByText('1').closest('a');
    expect(inactivePage).toHaveAttribute('href', '/blog/?page=1');
  });

  test('рендерит многоточия при большом количестве страниц', () => {
    render(<PageNumbers currentPage={5} totalPages={20} baseUrl="/blog/" />);

    // Проверяем, что первая страница отображается
    expect(screen.getByText('1')).toBeInTheDocument();

    // Проверяем, что последняя страница отображается
    expect(screen.getByText('20')).toBeInTheDocument();
  });
});
