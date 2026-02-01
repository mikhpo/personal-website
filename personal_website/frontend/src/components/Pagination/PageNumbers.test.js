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

  test('рендерит правильный диапазон страниц для текущей страницы в начале', () => {
    render(<PageNumbers currentPage={1} totalPages={10} baseUrl="/blog/" />);

    // Должны отображаться страницы 1, 2, 3, 4, 5
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();

    // Страница 6 не должна отображаться
    expect(screen.queryByText('6')).not.toBeInTheDocument();

    // Должно быть многоточие в конце
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  test('рендерит правильный диапазон страниц для текущей страницы в середине', () => {
    render(<PageNumbers currentPage={5} totalPages={10} baseUrl="/blog/" />);

    // Должны отображаться страницы 3, 4, 5 (активная), 6, 7
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();

    // Должны отображаться первая и последняя страницы
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  test('рендерит правильный диапазон страниц для текущей страницы в конце', () => {
    render(<PageNumbers currentPage={10} totalPages={10} baseUrl="/blog/" />);

    // Должны отображаться страницы 6, 7, 8, 9, 10
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('9')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();

    // Страница 5 не должна отображаться
    expect(screen.queryByText('5')).not.toBeInTheDocument();
  });
});
