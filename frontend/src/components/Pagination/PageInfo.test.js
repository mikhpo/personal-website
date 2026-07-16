import React from 'react';
import { render, screen } from '@testing-library/react';
import PageInfo from './PageInfo';

/**
 * Тесты для компонента PageInfo
 */
describe('PageInfo', () => {
  /**
   * Тест проверяет отображение информации о текущей странице
   */
  test('рендерит информацию о текущей странице', () => {
    render(<PageInfo currentPage={3} totalPages={5} />);

    expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что компонент не отображается при одной странице
   */
  test('не рендерится при одной странице', () => {
    const { container } = render(<PageInfo currentPage={1} totalPages={1} />);

    expect(container.firstChild).toBeNull();
  });

  /**
   * Тест проверяет правильное применение CSS-классов
   */
  test('применяет правильные CSS-классы', () => {
    render(<PageInfo currentPage={2} totalPages={5} />);

    const pageInfo = screen.getByText('страница 2 из 5');
    expect(pageInfo).toHaveClass('current');
  });
});
