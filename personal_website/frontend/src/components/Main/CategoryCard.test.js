/**
 * Тесты для компонента CategoryCard.
 *
 * Проверяет корректность отображения карточки категории с различными наборами данных,
 * включая минимальные и полные данные категории, обработку пустых значений,
 * правильность ссылок.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import CategoryCard from '@components/Main/CategoryCard';

describe('CategoryCard', () => {
  const minimalCategory = {
    id: 1,
    name: 'Разработка',
    slug: 'razrabotka',
  };

  const fullCategory = {
    id: 1,
    name: 'Разработка',
    slug: 'razrabotka',
    description: 'Статьи о разработке',
    image: '/media/blog/categories/dev.jpg',
  };

  /**
   * Проверяет, что компонент корректно рендерится с минимальным набором свойств.
   * Должно отображаться название категории.
   */
  test('рендерит с минимальными props', () => {
    render(<CategoryCard category={minimalCategory} />);
    expect(screen.getByText('Разработка')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно рендерится с полным набором свойств.
   * Должны отображаться название, описание и изображение категории.
   */
  test('рендерит с полными props', () => {
    render(<CategoryCard category={fullCategory} />);
    expect(screen.getByText('Разработка')).toBeInTheDocument();
    expect(screen.getByText('Статьи о разработке')).toBeInTheDocument();
    expect(screen.getByAltText('Разработка')).toBeInTheDocument();
  });

  /**
   * Проверяет, что изображение не отображается, если URL изображения пустой.
   * Компонент должен корректно обрабатывать отсутствие изображения.
   */
  test('не отображает изображение если image пустой', () => {
    render(<CategoryCard category={minimalCategory} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на категорию формируется с правильным URL.
   * Все ссылки в карточке должны вести на страницу категории.
   */
  test('ссылка на категорию имеет правильный URL', () => {
    render(<CategoryCard category={fullCategory} />);
    const links = screen.getAllByRole('link');
    links.forEach((link) => {
      expect(link).toHaveAttribute('href', '/blog/category/razrabotka/');
    });
  });

  /**
   * Проверяет, что описание не отображается при его отсутствии.
   */
  test('не отображает описание когда его нет', () => {
    render(<CategoryCard category={minimalCategory} />);
    expect(screen.queryByTestId('card-text')).not.toBeInTheDocument();
  });

  /**
   * Проверяет поведение компонента при пустом URL изображения.
   * При пустом значении image изображение не должно отображаться.
   */
  test('рендерит с пустой строкой в image', () => {
    const categoryWithEmptyImage = {
      ...fullCategory,
      image: '',
    };
    render(<CategoryCard category={categoryWithEmptyImage} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения специальных символов в названии.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в названии', () => {
    const categoryWithSpecialChars = {
      ...minimalCategory,
      name: 'Категория <>&"\'',
    };
    render(<CategoryCard category={categoryWithSpecialChars} />);
    expect(screen.getByText(categoryWithSpecialChars.name)).toBeInTheDocument();
  });
});
