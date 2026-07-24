/**
 * Тесты для компонента ArticleCard.
 *
 * Проверяет корректность отображения карточки статьи с различными наборами данных,
 * включая минимальные и полные данные статьи, усечение контента, правильность ссылок.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import ArticleCard from './ArticleCard';

describe('ArticleCard', () => {
  const minimalArticle = {
    id: 1,
    title: 'Тестовая статья',
  };

  const articleWithShortContent = {
    id: 2,
    title: 'Короткая статья',
    content: '<p>Это короткий текст статьи.</p>',
  };

  const generateLongContent = () => {
    const words = Array(250).fill('слово').join(' ');
    return `<p>${words}</p>`;
  };

  const articleWithLongContent = {
    id: 3,
    title: 'Длинная статья',
    content: generateLongContent(),
  };

  /**
   * Проверяет, что компонент корректно рендерится с минимальным набором свойств.
   * Должен отображаться заголовок статьи.
   */
  test('рендерит с минимальными props', () => {
    render(<ArticleCard article={minimalArticle} />);
    expect(screen.getByText('Тестовая статья')).toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на статью формируется с правильным URL.
   * Ссылка в заголовке должна вести на страницу статьи.
   */
  test('ссылка на статью имеет правильный URL', () => {
    render(<ArticleCard article={minimalArticle} />);
    const link = screen.getByText('Тестовая статья');
    expect(link.closest('a')).toHaveAttribute('href', '/blog/1/');
  });

  /**
   * Проверяет, что ссылка "Читать дальше" не отображается при отсутствии контента.
   * Компонент должен корректно обрабатывать отсутствие текста статьи.
   */
  test('не отображает ссылку "Читать дальше" если контента нет', () => {
    render(<ArticleCard article={minimalArticle} />);
    expect(screen.queryByText('Читать дальше')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно отображает полный контент короткой статьи.
   * При количестве слов ≤ 200 должен отображаться весь текст.
   */
  test('отображает полный контент короткой статьи', () => {
    render(<ArticleCard article={articleWithShortContent} />);
    expect(screen.getByText('Это короткий текст статьи.')).toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка "Читать дальше" не отображается для короткой статьи.
   * При количестве слов ≤ 200 усечение не применяется.
   */
  test('не отображает ссылку "Читать дальше" для короткой статьи', () => {
    render(<ArticleCard article={articleWithShortContent} />);
    expect(screen.queryByText('Читать дальше')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что для длинной статьи отображается ссылка "Читать дальше".
   * При количестве слов > 200 должна появиться дополнительная ссылка.
   */
  test('отображает ссылку "Читать дальше" для длинной статьи', () => {
    render(<ArticleCard article={articleWithLongContent} />);
    expect(screen.getByText('Читать дальше')).toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка "Читать дальше" ведет на страницу статьи.
   * Атрибут href должен соответствовать URL статьи.
   */
  test('ссылка "Читать дальше" имеет правильный URL', () => {
    render(<ArticleCard article={articleWithLongContent} />);
    const link = screen.getByText('Читать дальше');
    expect(link).toHaveAttribute('href', '/blog/3/');
  });

  /**
   * Проверяет корректность отображения статьи с пустым контентом.
   * Компонент должен корректно обрабатывать пустую строку в поле content.
   */
  test('рендерит с пустым контентом', () => {
    const articleWithEmptyContent = {
      id: 4,
      title: 'Пустая статья',
      content: '',
    };
    render(<ArticleCard article={articleWithEmptyContent} />);
    expect(screen.queryByText('Читать дальше')).not.toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения специальных символов в заголовке.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в заголовке', () => {
    const articleWithSpecialChars = {
      id: 5,
      title: 'Статья с <символами> & "спецсимволами"',
    };
    render(<ArticleCard article={articleWithSpecialChars} />);
    expect(screen.getByText('Статья с <символами> & "спецсимволами"')).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения статьи с длинным заголовком.
   * Компонент должен корректно отображать заголовки произвольной длины.
   */
  test('рендерит с длинным заголовком', () => {
    const longTitle = 'О'.repeat(200);
    const articleWithLongTitle = {
      id: 6,
      title: longTitle,
    };
    render(<ArticleCard article={articleWithLongTitle} />);
    expect(screen.getByText(longTitle)).toBeInTheDocument();
  });
});
