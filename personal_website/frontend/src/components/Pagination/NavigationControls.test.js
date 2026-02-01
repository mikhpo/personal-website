import React from 'react';
import { render, screen } from '@testing-library/react';
import NavigationControls from './NavigationControls';

/**
 * Тесты для компонента NavigationControls
 *
 * @description
 * Компонент NavigationControls отвечает за отображение кнопок навигации (Первая/Предыдущая/Следующая/Последняя)
 * в системе пагинации. Тесты проверяют корректность отображения кнопок, формирования ссылок
 * и состояния disabled для граничных случаев (первая и последняя страницы).
 */
describe('NavigationControls', () => {
  /**
   * Тест проверяет, что кнопка "Первая" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе со второй страницы на первую формируется
   * корректная ссылка с параметром page=1
   */
  test('рендерит кнопку "первая" с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={2}
        totalPages={5}
        baseUrl="/blog/"
        type="first"
      />
    );

    const firstButton = screen.getByText('первая');
    expect(firstButton).toHaveAttribute('href', '/blog/?page=1');
    expect(firstButton).toHaveClass('btn', 'btn-outline-dark', 'me-1');
  });

  /**
   * Тест проверяет, что кнопка "Первая" отключена на первой странице
   *
   * @description
   * Тест проверяет, что на первой странице кнопка "Первая" получает
   * атрибут disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку "первая" на первой странице', () => {
    render(
      <NavigationControls
        currentPage={1}
        totalPages={5}
        baseUrl="/blog/"
        type="first"
      />
    );

    const firstButton = screen.getByText('первая');
    expect(firstButton).toBeDisabled();
  });

  /**
   * Тест проверяет, что кнопка "Предыдущая" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе со второй страницы на первую формируется
   * корректная ссылка с параметром page=1
   */
  test('рендерит кнопку "предыдущая" с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={2}
        totalPages={5}
        baseUrl="/blog/"
        type="prev"
      />
    );

    const prevButton = screen.getByText('предыдущая');
    expect(prevButton).toHaveAttribute('href', '/blog/?page=1');
    expect(prevButton).toHaveClass('btn', 'btn-outline-dark', 'me-1');
  });

  /**
   * Тест проверяет, что кнопка "Предыдущая" отключена на первой странице
   *
   * @description
   * Тест проверяет, что на первой странице кнопка "Предыдущая" получает
   * атрибут disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку "предыдущая" на первой странице', () => {
    render(
      <NavigationControls
        currentPage={1}
        totalPages={5}
        baseUrl="/blog/"
        type="prev"
      />
    );

    const prevButton = screen.getByText('предыдущая');
    expect(prevButton).toBeDisabled();
  });

  /**
   * Тест проверяет, что кнопка "Следующая" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе со второй страницы на третью формируется
   * корректная ссылка с параметром page=3
   */
  test('рендерит кнопку "следующая" с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={2}
        totalPages={5}
        baseUrl="/blog/"
        type="next"
      />
    );

    const nextButton = screen.getByText('следующая');
    expect(nextButton).toHaveAttribute('href', '/blog/?page=3');
    expect(nextButton).toHaveClass('btn', 'btn-outline-dark', 'ms-1');
  });

  /**
   * Тест проверяет, что кнопка "Следующая" отключена на последней странице
   *
   * @description
   * Тест проверяет, что на последней странице кнопка "Следующая" получает
   * атрибут disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку "следующая" на последней странице', () => {
    render(
      <NavigationControls
        currentPage={5}
        totalPages={5}
        baseUrl="/blog/"
        type="next"
      />
    );

    const nextButton = screen.getByText('следующая');
    expect(nextButton).toBeDisabled();
  });

  /**
   * Тест проверяет, что кнопка "Последняя" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе с четвертой страницы на пятую формируется
   * корректная ссылка с параметром page=5
   */
  test('рендерит кнопку "последняя" с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={4}
        totalPages={5}
        baseUrl="/blog/"
        type="last"
      />
    );

    const lastButton = screen.getByText('последняя');
    expect(lastButton).toHaveAttribute('href', '/blog/?page=5');
    expect(lastButton).toHaveClass('btn', 'btn-outline-dark', 'ms-1');
  });

  /**
   * Тест проверяет, что кнопка "Последняя" отключена на последней странице
   *
   * @description
   * Тест проверяет, что на последней странице кнопка "Последняя" получает
   * атрибут disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку "последняя" на последней странице', () => {
    render(
      <NavigationControls
        currentPage={5}
        totalPages={5}
        baseUrl="/blog/"
        type="last"
      />
    );

    const lastButton = screen.getByText('последняя');
    expect(lastButton).toBeDisabled();
  });
});
