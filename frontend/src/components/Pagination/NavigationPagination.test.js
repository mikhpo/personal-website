import React from 'react';
import { render, screen } from '@testing-library/react';
import NavigationPagination from './NavigationPagination';

/**
 * Тесты для компонента NavigationPagination
 */
describe('NavigationPagination', () => {
  /**
   * Тест проверяет отображение всех элементов навигационной пагинации
   */
  test('рендерит все элементы навигационной пагинации', () => {
    render(<NavigationPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('первая')).toBeInTheDocument();
    expect(screen.getByText('предыдущая')).toBeInTheDocument();
    expect(screen.getByText('следующая')).toBeInTheDocument();
    expect(screen.getByText('последняя')).toBeInTheDocument();
    expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
  });

  /**
   * Тест проверяет правильную структуру компонента
   */
  test('имеет правильную структуру', () => {
    const { container } = render(<NavigationPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(container.querySelector('.step-links')).toBeInTheDocument();
    expect(container.querySelector('div')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что все кнопки имеют правильные стили
   */
  test('все кнопки имеют правильные стили', () => {
    render(<NavigationPagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const buttons = screen.getAllByRole('link');
    buttons.forEach(button => {
      expect(button).toHaveClass('btn', 'btn-outline-dark');
    });
  });

  /**
   * Тест проверяет, что кнопки "первая" и "предыдущая" не рендерятся на первой странице
   */
  test('не рендерит кнопки "первая" и "предыдущая" на первой странице', () => {
    render(<NavigationPagination currentPage={1} totalPages={5} baseUrl="/blog/" />);

    expect(screen.queryByText('первая')).not.toBeInTheDocument();
    expect(screen.queryByText('предыдущая')).not.toBeInTheDocument();
    expect(screen.getByText('следующая')).toBeInTheDocument();
    expect(screen.getByText('последняя')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что кнопки "следующая" и "последняя" не рендерятся на последней странице
   */
  test('не рендерит кнопки "следующая" и "последняя" на последней странице', () => {
    render(<NavigationPagination currentPage={5} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('первая')).toBeInTheDocument();
    expect(screen.getByText('предыдущая')).toBeInTheDocument();
    expect(screen.queryByText('следующая')).not.toBeInTheDocument();
    expect(screen.queryByText('последняя')).not.toBeInTheDocument();
  });
});
