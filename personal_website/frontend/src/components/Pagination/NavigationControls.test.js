import React from 'react';
import { render, screen } from '@testing-library/react';
import NavigationControls from './NavigationControls';

/**
 * Тесты для компонента NavigationControls
 *
 * @description
 * Компонент NavigationControls отвечает за отображение кнопок навигации (Предыдущая/Следующая)
 * в системе пагинации. Тесты проверяют корректность отображения кнопок, формирования ссылок
 * и состояния disabled для граничных случаев (первая и последняя страницы).
 */
describe('NavigationControls', () => {
  /**
   * Проверяет, что кнопка "Предыдущая" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе со второй страницы на первую формируется
   * корректная ссылка с параметром page=1
   */
  test('рендерит кнопку Previous с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={2}
        totalPages={5}
        baseUrl="/blog/"
        type="prev"
      />
    );

    const prevButton = screen.getByText('Previous').closest('a');
    expect(prevButton).toHaveAttribute('href', '/blog/?page=1');
  });

  /**
   * Проверяет, что кнопка "Предыдущая" отключена на первой странице
   *
   * @description
   * Тест проверяет, что на первой странице кнопка "Предыдущая" получает
   * класс disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку Previous на первой странице', () => {
    render(
      <NavigationControls
        currentPage={1}
        totalPages={5}
        baseUrl="/blog/"
        type="prev"
      />
    );

    const prevButton = screen.getByText('Previous').closest('li');
    expect(prevButton).toHaveClass('disabled');
  });

  /**
   * Проверяет, что кнопка "Следующая" отображается с правильной ссылкой
   *
   * @description
   * Тест проверяет, что при переходе со второй страницы на третью формируется
   * корректная ссылка с параметром page=3
   */
  test('рендерит кнопку Next с правильной ссылкой', () => {
    render(
      <NavigationControls
        currentPage={2}
        totalPages={5}
        baseUrl="/blog/"
        type="next"
      />
    );

    const nextButton = screen.getByText('Next').closest('a');
    expect(nextButton).toHaveAttribute('href', '/blog/?page=3');
  });

  /**
   * Проверяет, что кнопка "Следующая" отключена на последней странице
   *
   * @description
   * Тест проверяет, что на последней странице кнопка "Следующая" получает
   * класс disabled, что делает её неактивной для пользователя
   */
  test('отключает кнопку Next на последней странице', () => {
    render(
      <NavigationControls
        currentPage={5}
        totalPages={5}
        baseUrl="/blog/"
        type="next"
      />
    );

    const nextButton = screen.getByText('Next').closest('li');
    expect(nextButton).toHaveClass('disabled');
  });
});
