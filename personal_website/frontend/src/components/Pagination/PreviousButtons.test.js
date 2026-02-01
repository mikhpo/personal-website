import React from 'react';
import { render, screen } from '@testing-library/react';
import PreviousButtons from './PreviousButtons';

/**
 * Тесты для компонента PreviousButtons
 */
describe('PreviousButtons', () => {
  /**
   * Тест проверяет отображение кнопок "первая" и "предыдущая"
   */
  test('рендерит кнопки "первая" и "предыдущая"', () => {
    render(<PreviousButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('первая')).toBeInTheDocument();
    expect(screen.getByText('предыдущая')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что кнопки имеют правильные стили
   */
  test('кнопки имеют правильные стили', () => {
    render(<PreviousButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const firstButton = screen.getByText('первая');
    const prevButton = screen.getByText('предыдущая');

    expect(firstButton).toHaveClass('btn', 'btn-outline-dark');
    expect(prevButton).toHaveClass('btn', 'btn-outline-dark');
  });

  /**
   * Тест проверяет, что кнопки не отображаются на первой странице
   */
  test('не рендерит кнопки на первой странице', () => {
    const { container } = render(<PreviousButtons currentPage={1} totalPages={5} baseUrl="/blog/" />);

    expect(container.firstChild).toBeNull();
  });

  /**
   * Тест проверяет формирование правильных ссылок
   */
  test('формирует правильные ссылки для кнопок', () => {
    render(<PreviousButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const firstButton = screen.getByText('первая');
    const prevButton = screen.getByText('предыдущая');

    expect(firstButton).toHaveAttribute('href', '/blog/?page=1');
    expect(prevButton).toHaveAttribute('href', '/blog/?page=2');
  });
});
