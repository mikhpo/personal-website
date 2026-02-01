import React from 'react';
import { render } from '@testing-library/react';
import { renderPaginationItem, renderNavigationButton } from './paginationRenderers';

/**
 * Моки зависимостей
 *
 *  Для тестирования функций рендеринга создаются моки зависимостей:
 * - getPageUrl: чтобы получить фиксированные URL вида "/blog/?page=N"
 * - getButtonText: чтобы получить фиксированные тексты кнопок ("первая", "предыдущая" и т.д.)
 * - getButtonClassName: чтобы получить фиксированные CSS-классы
 * - isButtonDisabled: чтобы контролировать состояние отключения кнопок
 * - getButtonHref: чтобы получить фиксированные URL для кнопок
 *
 * Это позволяет тестировать рендеринг независимо от реализации вспомогательных функций.
 */
// Мокаем зависимости
jest.mock('./paginationHelpers', () => ({
  /**
   * Возвращает "/baseUrl?page=N"
   */
  getPageUrl: jest.fn((baseUrl, page) => `${baseUrl}?page=${page}`)
}));

jest.mock('./buttonStates', () => ({
  /**
   * Возвращает текст кнопки по типу
   */
  getButtonText: jest.fn((type) => {
    const texts = {
      'first': 'первая',
      'prev': 'предыдущая',
      'next': 'следующая',
      'last': 'последняя'
    };
    return texts[type] || '';
  }),

  /**
   * Возвращает CSS-классы кнопки по типу
   */
  getButtonClassName: jest.fn((type) => {
    const classes = {
      'first': 'btn btn-outline-dark me-1',
      'prev': 'btn btn-outline-dark me-1',
      'next': 'btn btn-outline-dark ms-1',
      'last': 'btn btn-outline-dark ms-1'
    };
    return classes[type] || 'btn btn-outline-dark';
  }),

  /**
   * Возвращает true если кнопка должна быть отключена
   */
  isButtonDisabled: jest.fn((type, currentPage, totalPages) => {
    if ((type === 'first' || type === 'prev') && currentPage === 1) return true;
    if ((type === 'next' || type === 'last') && currentPage === totalPages) return true;
    return false;
  }),

  /**
   * Возвращает URL для кнопки или undefined если кнопка отключена
   */
  getButtonHref: jest.fn((type, currentPage, totalPages, baseUrl) => {
    if ((type === 'first' || type === 'prev') && currentPage === 1) return undefined;
    if ((type === 'next' || type === 'last') && currentPage === totalPages) return undefined;

    switch (type) {
      case 'first': return `${baseUrl}?page=1`;
      case 'prev': return `${baseUrl}?page=${currentPage - 1}`;
      case 'next': return `${baseUrl}?page=${currentPage + 1}`;
      case 'last': return `${baseUrl}?page=${totalPages}`;
      default: return undefined;
    }
  })
}));

/**
 * Тесты для утилит рендеринга элементов пагинации
 */
describe('paginationRenderers', () => {
  /**
   * Тесты для функции renderPaginationItem
   */
  describe('renderPaginationItem', () => {
    /**
     * Проверяет рендеринг первой страницы
     * Ожидается: ссылка с href="/blog/?page=1" и текстом "1"
     */
    test('рендерит элемент первой страницы', () => {
      const { container } = render(
        renderPaginationItem('first-page', undefined, 3, 5, '/blog/')
      );

      const item = container.querySelector('a');
      expect(item).toBeInTheDocument();
      expect(item).toHaveAttribute('href', '/blog/?page=1');
      expect(item.textContent).toBe('1');
    });

    /**
     * Проверяет рендеринг многоточия в начале
     * Ожидается: элемент .page-item с классом disabled
     */
    test('рендерит многоточие в начале', () => {
      const { container } = render(
        renderPaginationItem('ellipsis-start', undefined, 3, 5, '/blog/')
      );

      const ellipsis = container.querySelector('.page-item');
      expect(ellipsis).toBeInTheDocument();
      expect(ellipsis).toHaveClass('disabled');
    });

    /**
     * Проверяет рендеринг активной страницы
     * Ожидается: элемент .page-item с классом active и без ссылки
     */
    test('рендерит элемент страницы', () => {
      const { container } = render(
        renderPaginationItem('page', 3, 3, 5, '/blog/')
      );

      const item = container.querySelector('.page-item');
      expect(item).toBeInTheDocument();
      expect(item.textContent).toContain('3');
      expect(item).toHaveClass('active');

      const link = item.querySelector('a');
      expect(link).toBeNull();
    });

    /**
     * Проверяет рендеринг неактивной страницы
     * Ожидается: ссылка с href="/blog/?page=2"
     */
    test('рендерит элемент неактивной страницы со ссылкой', () => {
      const { container } = render(
        renderPaginationItem('page', 2, 3, 5, '/blog/')
      );

      const item = container.querySelector('a');
      expect(item).toBeInTheDocument();
      expect(item).toHaveAttribute('href', '/blog/?page=2');
    });

    /**
     * Проверяет рендеринг многоточия в конце
     * Ожидается: элемент .page-item с классом disabled
     */
    test('рендерит многоточие в конце', () => {
      const { container } = render(
        renderPaginationItem('ellipsis-end', undefined, 3, 5, '/blog/')
      );

      const ellipsis = container.querySelector('.page-item');
      expect(ellipsis).toBeInTheDocument();
      expect(ellipsis).toHaveClass('disabled');
    });

    /**
     * Проверяет рендеринг последней страницы
     * Ожидается: ссылка с href="/blog/?page=5" и текстом "5"
     */
    test('рендерит элемент последней страницы', () => {
      const { container } = render(
        renderPaginationItem('last-page', undefined, 3, 5, '/blog/')
      );

      const item = container.querySelector('a');
      expect(item).toBeInTheDocument();
      expect(item).toHaveAttribute('href', '/blog/?page=5');
      expect(item.textContent).toBe('5');
    });

    /**
     * Проверяет обработку неизвестного типа
     * Ожидается: null
     */
    test('возвращает null для неизвестного типа элемента', () => {
      const result = renderPaginationItem('unknown', undefined, 3, 5, '/blog/');
      expect(result).toBeNull();
    });
  });

  /**
   * Тесты для функции renderNavigationButton
   */
  describe('renderNavigationButton', () => {
    /**
     * Проверяет рендеринг кнопки "первая"
     * Ожидается: ссылка с href="/blog/?page=1", текстом "первая" и классами
     */
    test('рендерит кнопку "первая"', () => {
      const { container } = render(
        renderNavigationButton('first', 3, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('href', '/blog/?page=1');
      expect(button.textContent).toBe('первая');
      expect(button).toHaveClass('btn', 'btn-outline-dark', 'me-1');
    });

    /**
     * Проверяет отключенную кнопку "первая" на первой странице
     * Ожидается: ссылка без href и с атрибутом disabled
     */
    test('рендерит отключенную кнопку "первая" на первой странице', () => {
      const { container } = render(
        renderNavigationButton('first', 1, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).not.toHaveAttribute('href');
      expect(button).toHaveAttribute('disabled');
    });

    /**
     * Проверяет рендеринг кнопки "предыдущая"
     * Ожидается: ссылка с href="/blog/?page=2", текстом "предыдущая" и классами
     */
    test('рендерит кнопку "предыдущая"', () => {
      const { container } = render(
        renderNavigationButton('prev', 3, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('href', '/blog/?page=2');
      expect(button.textContent).toBe('предыдущая');
      expect(button).toHaveClass('btn', 'btn-outline-dark', 'me-1');
    });

    /**
     * Проверяет отключенную кнопку "предыдущая" на первой странице
     * Ожидается: ссылка без href и с атрибутом disabled
     */
    test('рендерит отключенную кнопку "предыдущая" на первой странице', () => {
      const { container } = render(
        renderNavigationButton('prev', 1, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).not.toHaveAttribute('href');
      expect(button).toHaveAttribute('disabled');
    });

    /**
     * Проверяет рендеринг кнопки "следующая"
     * Ожидается: ссылка с href="/blog/?page=4", текстом "следующая" и классами
     */
    test('рендерит кнопку "следующая"', () => {
      const { container } = render(
        renderNavigationButton('next', 3, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('href', '/blog/?page=4');
      expect(button.textContent).toBe('следующая');
      expect(button).toHaveClass('btn', 'btn-outline-dark', 'ms-1');
    });

    /**
     * Проверяет отключенную кнопку "следующая" на последней странице
     * Ожидается: ссылка без href и с атрибутом disabled
     */
    test('рендерит отключенную кнопку "следующая" на последней странице', () => {
      const { container } = render(
        renderNavigationButton('next', 5, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).not.toHaveAttribute('href');
      expect(button).toHaveAttribute('disabled');
    });

    /**
     * Проверяет рендеринг кнопки "последняя"
     * Ожидается: ссылка с href="/blog/?page=5", текстом "последняя" и классами
     */
    test('рендерит кнопку "последняя"', () => {
      const { container } = render(
        renderNavigationButton('last', 3, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('href', '/blog/?page=5');
      expect(button.textContent).toBe('последняя');
      expect(button).toHaveClass('btn', 'btn-outline-dark', 'ms-1');
    });

    /**
     * Проверяет отключенную кнопку "последняя" на последней странице
     * Ожидается: ссылка без href и с атрибутом disabled
     */
    test('рендерит отключенную кнопку "последняя" на последней странице', () => {
      const { container } = render(
        renderNavigationButton('last', 5, 5, '/blog/')
      );

      const button = container.querySelector('a');
      expect(button).toBeInTheDocument();
      expect(button).not.toHaveAttribute('href');
      expect(button).toHaveAttribute('disabled');
    });
  });
});
