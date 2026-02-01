import React from 'react';
import { render, screen } from '@testing-library/react';
import Pagination from './Pagination';

/**
 * Тесты для компонента пагинации
 *
 * @description
 * Набор тестов для проверки корректности работы компонента пагинации,
 * включая отображение элементов, обработку граничных случаев
 * и правильность формирования ссылок.
 */
describe('Pagination', () => {
  /**
   * Тест проверяет, что компонент не отображается при наличии только одной страницы
   *
   * @description
   * При totalPages равном 1 компонент должен возвращать null,
   * так как пагинация не требуется.
   */
  test('не рендерится при одной странице', () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={1} baseUrl="/blog/" />
    );
    expect(container.firstChild).toBeNull();
  });

  /**
   * Тест проверяет корректность отображения номеров страниц
   *
   * @description
   * Компонент должен отображать первую и последнюю страницы
   * при наличии нескольких страниц.
   */
  test('рендерит правильное количество страниц', () => {
    render(<Pagination currentPage={1} totalPages={5} baseUrl="/blog/" />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  /**
   * Тест проверяет отключение кнопки "Предыдущая" на первой странице
   *
   * @description
   * При currentPage равном 1 кнопка "Предыдущая" должна иметь класс 'disabled'.
   */
  test('отключает кнопку Previous на первой странице', () => {
    render(<Pagination currentPage={1} totalPages={5} baseUrl="/blog/" />);

    const prevButton = screen.getByText('Previous').closest('li');
    expect(prevButton).toHaveClass('disabled');
  });

  /**
   * Тест проверяет отключение кнопки "Следующая" на последней странице
   *
   * @description
   * При currentPage равном totalPages кнопка "Следующая" должна иметь класс 'disabled'.
   */
  test('отключает кнопку Next на последней странице', () => {
    render(<Pagination currentPage={5} totalPages={5} baseUrl="/blog/" />);

    const nextButton = screen.getByText('Next').closest('li');
    expect(nextButton).toHaveClass('disabled');
  });
});
