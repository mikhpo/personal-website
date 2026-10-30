/**
 * Тесты для компонента ArticleCard.
 *
 * Проверяет корректность отображения карточки статьи с различными наборами данных,
 * включая минимальные и полные данные статьи, усечение контента, правильность ссылок.
 */

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import ArticleCard from './ArticleCard';
import { makeArticle } from '@test-utils';

describe('ArticleCard', () => {
  // url undefined проверяет fallback карточки на /blog/{id}/
  const minimalArticle = makeArticle({
    id: 1,
    title: 'Тестовая статья',
    url: undefined,
  });

  const articleWithShortContent = makeArticle({
    id: 2,
    title: 'Короткая статья',
    content: '<p>Это короткий текст статьи.</p>',
  });

  const generateLongContent = () => {
    const words = Array(250).fill('слово').join(' ');
    return `<p>${words}</p>`;
  };

  const articleWithLongContent = makeArticle({
    id: 3,
    title: 'Длинная статья',
    content: generateLongContent(),
    url: undefined,
  });

  /**
   * Длинная статья с фотографией в начале: изображение находится до точки
   * обрезки и должно попасть в превью.
   */
  const articleWithPhotoAndLongContent = makeArticle({
    id: 7,
    title: 'Статья с фотографией',
    content: '<p><img src="/media/photo.jpg" alt="Фотография" /></p><p>' + generateLongContent() + '</p>',
    url: undefined,
  });

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
    const articleWithEmptyContent = makeArticle({
      id: 4,
      title: 'Пустая статья',
      content: '',
    });
    render(<ArticleCard article={articleWithEmptyContent} />);
    expect(screen.queryByText('Читать дальше')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что фотография из начала статьи видна в превью длинной статьи.
   * Изображение находится до точки обрезки и попадает в карточку.
   */
  test('отображает фотографию в превью длинной статьи', () => {
    render(<ArticleCard article={articleWithPhotoAndLongContent} />);
    const photo = screen.getByRole('img', { name: 'Фотография' });
    expect(photo).toHaveAttribute('src', '/media/photo.jpg');
  });

  /**
   * Проверяет, что HTML-форматирование короткой статьи сохраняется в превью:
   * контент рендерится как разметка, а не как текст.
   */
  test('отображает HTML-форматирование в превью короткой статьи', () => {
    const articleWithFormattedContent = makeArticle({
      id: 8,
      title: 'Форматированная статья',
      content: '<p>Это <b>жирный</b> текст статьи.</p>',
    });
    const { container } = render(<ArticleCard article={articleWithFormattedContent} />);
    expect(container.querySelector('.card-text b')).toHaveTextContent('жирный');
  });

  /**
   * Проверяет, что длинная статья обрезается до 50 слов: начало текста в
   * превью есть, хвост - нет, разметка замкнута.
   */
  test('обрезает длинную статью до 50 слов с замкнутой разметкой', () => {
    const numberedWords = Array.from({ length: 250 }, (_, index) => `слово${index + 1}`).join(' ');
    const article = makeArticle({
      id: 9,
      title: 'Нумерованная статья',
      content: `<p>${numberedWords}</p>`,
      url: undefined,
    });
    const { container } = render(<ArticleCard article={article} />);
    const preview = container.querySelector('.card-text');
    expect(preview).toHaveTextContent('слово1');
    expect(preview).toHaveTextContent('слово50');
    expect(preview).not.toHaveTextContent('слово51');
    expect(preview?.innerHTML.endsWith('</p>')).toBe(true);
  });

  /**
   * Проверяет корректность отображения специальных символов в заголовке.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в заголовке', () => {
    const articleWithSpecialChars = makeArticle({
      id: 5,
      title: 'Статья с <символами> & "спецсимволами"',
    });
    render(<ArticleCard article={articleWithSpecialChars} />);
    expect(screen.getByText('Статья с <символами> & "спецсимволами"')).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения статьи с длинным заголовком.
   * Компонент должен корректно отображать заголовки произвольной длины.
   */
  test('рендерит с длинным заголовком', () => {
    const longTitle = 'О'.repeat(200);
    const articleWithLongTitle = makeArticle({
      id: 6,
      title: longTitle,
    });
    render(<ArticleCard article={articleWithLongTitle} />);
    expect(screen.getByText(longTitle)).toBeInTheDocument();
  });
});
