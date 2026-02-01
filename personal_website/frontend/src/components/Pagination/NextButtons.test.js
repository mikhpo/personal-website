import React from 'react';
import { render, screen } from '@testing-library/react';
import NextButtons from './NextButtons';

/**
 * Тесты для компонента NextButtons
 */
describe('NextButtons', () => {
  /**
   * Тест проверяет отображение кнопок "следующая" и "последняя"
   */
  test('рендерит кнопки "следующая" и "последняя"', () => {
    render(<NextButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('следующая')).toBeInTheDocument();
    expect(screen.getByText('последняя')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что кнопки имеют правильные стили
   */
  test('кнопки имеют правильные стили', () => {
    render(<NextButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const nextButton = screen.getByText('следующая');
    const lastButton = screen.getByText('последняя');

    expect(nextButton).toHaveClass('btn', 'btn-outline-dark');
    expect(lastButton).toHaveClass('btn', 'btn-outline-dark');
  });

  /**
   * Тест проверяет, что кнопки не отображаются на последней странице
   */
  test('не рендерит кнопки на последней странице', () => {
    const { container } = render(<NextButtons currentPage={5} totalPages={5} baseUrl="/blog/" />);

    expect(container.firstChild).toBeNull();
  });

  /**
   * Тест проверяет формирование правильных ссылок
   */
  test('формирует правильные ссылки для кнопок', () => {
    render(<NextButtons currentPage={3} totalPages={5} baseUrl="/blog/" />);

    const nextButton = screen.getByText('следующая');
    const lastButton = screen.getByText('последняя');

    expect(nextButton).toHaveAttribute('href', '/blog/?page=4');
    expect(lastButton).toHaveAttribute('href', '/blog/?page=5');
  });
});
