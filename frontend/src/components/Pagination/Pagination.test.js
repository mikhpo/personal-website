import React from 'react';
import { render, screen } from '@testing-library/react';
import Pagination from './Pagination';

describe('Pagination', () => {
  test('не рендерится при одной странице', () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={1} baseUrl="/blog/" />
    );
    expect(container.firstChild).toBeNull();
  });

  describe('навигационная пагинация', () => {
    test('рендерит навигационную пагинацию по умолчанию', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

      expect(screen.getByText('первая')).toBeInTheDocument();
      expect(screen.getByText('предыдущая')).toBeInTheDocument();
      expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
      expect(screen.getByText('следующая')).toBeInTheDocument();
      expect(screen.getByText('последняя')).toBeInTheDocument();
    });

    test('рендерит навигационную пагинацию с явным указанием типа', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="navigation" />);

      expect(screen.getByText('первая')).toBeInTheDocument();
      expect(screen.getByText('предыдущая')).toBeInTheDocument();
      expect(screen.getByText('страница 3 из 5')).toBeInTheDocument();
      expect(screen.getByText('следующая')).toBeInTheDocument();
      expect(screen.getByText('последняя')).toBeInTheDocument();
    });
  });

  describe('пагинация с номерами страниц', () => {
    test('рендерит пагинацию с номерами страниц', () => {
      render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="numbers" />);

      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('4')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
    });

    test('рендерит многоточия при большом количестве страниц', () => {
      render(<Pagination currentPage={5} totalPages={20} baseUrl="/blog/" type="numbers" />);

      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
    });
  });

  describe('структура компонента', () => {
    test('имеет правильную структуру контейнеров в навигационной пагинации', () => {
      const { container } = render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" />);

      expect(container.querySelector('.container')).toBeInTheDocument();
      expect(container.querySelector('.pagination')).toBeInTheDocument();
    });

    test('имеет правильную структуру контейнеров в пагинации с номерами', () => {
      const { container } = render(<Pagination currentPage={3} totalPages={5} baseUrl="/blog/" type="numbers" />);

      expect(container.querySelector('.container')).toBeInTheDocument();
      expect(container.querySelector('.pagination')).toBeInTheDocument();
    });
  });
});
