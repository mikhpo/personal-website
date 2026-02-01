import React from 'react';
import { render, screen } from '@testing-library/react';
import Pagination from './Pagination';

/**
 * Тесты для основного компонента пагинации
 */
describe('Pagination', () => {
  /**
   * Тест проверяет, что компонент не отображается при наличии только одной страницы
   */
  test('не рендерится при одной странице', () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={1} baseUrl="/blog/" />
    );
    expect(container.firstChild).toBeNull();
  });

  /**
   * Тесты для навигационной пагинации (по умолчанию)
   */
  describe('навигационная пагинация', () => {
    /**
     * Тест проверяет отображение навигационной пагинации по умолчанию
     */
    test('рендерит навигационную пагинацию по умолчанию', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

      expect(screen.getByText('первая')).toBeInTheDocument();
      expect(screen.getByText('предыдущая')).toBeInTheDocument();
      expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
      expect(screen.getByText('следующая')).toBeInTheDocument();
      expect(screen.getByText('последняя')).toBeInTheDocument();
    });

    /**
     * Тест проверяет отображение навигационной пагинации с явным указанием типа
     */
    test('рендерит навигационную пагинацию с явным указанием типа', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="navigation" />);

      expect(screen.getByText('первая')).toBeInTheDocument();
      expect(screen.getByText('предыдущая')).toBeInTheDocument();
      expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
      expect(screen.getByText('следующая')).toBeInTheDocument();
      expect(screen.getByText('последняя')).toBeInTheDocument();
    });
  });

  /**
   * Тесты для пагинации с номерами страниц
   */
  describe('пагинация с номерами страниц', () => {
    /**
     * Тест проверяет отображение пагинации с номерами страниц
     */
    test('рендерит пагинацию с номерами страниц', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="numbers" />);

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
      render(<Pagination currentPage={5} totalPages={20} baseUrl="/blog/" type="numbers" />);

      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
    });
  });

  /**
   * Тесты для структуры компонента
   */
  describe('структура компонента', () => {
    /**
     * Тест проверяет наличие контейнеров в навигационной пагинации
     */
    test('имеет правильную структуру контейнеров в навигационной пагинации', () => {
      const { container } = render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

      expect(container.querySelector('.container')).toBeInTheDocument();
      expect(container.querySelector('.pagination')).toBeInTheDocument();
    });

    /**
     * Тест проверяет наличие контейнеров в пагинации с номерами
     */
    test('имеет правильную структуру контейнеров в пагинации с номерами', () => {
      const { container } = render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="numbers" />);

      expect(container.querySelector('.container')).toBeInTheDocument();
      expect(container.querySelector('.pagination')).toBeInTheDocument();
    });
  });
});
