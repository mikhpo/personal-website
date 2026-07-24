/**
 * Тесты для компонента SeriesCard.
 *
 * Проверяет корректность отображения карточки серии с различными наборами данных,
 * включая минимальные и полные данные серии, обработку пустых значений,
 * правильность ссылок и изображений.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import SeriesCard from '@components/Main/SeriesCard';

describe('SeriesCard', () => {
  const minimalSeries = {
    id: 1,
    name: 'Лангтанг-трек',
    slug: 'langtang-trek',
  };

  const fullSeries = {
    id: 1,
    name: 'Лангтанг-трек',
    slug: 'langtang-trek',
    description: 'Поход в Непале',
    image: '/media/blog/series/langtang.jpg',
  };

  /**
   * Проверяет, что компонент корректно рендерится с полным набором свойств.
   * Должны отображаться название, описание и изображение серии.
   */
  test('рендерит с полными props', () => {
    render(<SeriesCard series={fullSeries} />);
    expect(screen.getByText('Лангтанг-трек')).toBeInTheDocument();
    expect(screen.getByText('Поход в Непале')).toBeInTheDocument();
    expect(screen.getByAltText('Лангтанг-трек')).toBeInTheDocument();
  });

  /**
   * Проверяет, что изображение не отображается, если URL изображения пустой.
   * Компонент должен корректно обрабатывать отсутствие изображения.
   */
  test('не отображает изображение если image пустой', () => {
    render(<SeriesCard series={minimalSeries} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на серию формируется с правильным URL.
   * Все ссылки в карточке должны вести на страницу серии.
   */
  test('ссылка на серию имеет правильный URL', () => {
    render(<SeriesCard series={fullSeries} />);
    const links = screen.getAllByRole('link');
    links.forEach((link) => {
      expect(link).toHaveAttribute('href', '/blog/series/langtang-trek/');
    });
  });

  /**
   * Проверяет, что изображение имеет правильный источник.
   * Атрибут src изображения должен соответствовать URL из данных серии.
   */
  test('изображение имеет правильный src', () => {
    render(<SeriesCard series={fullSeries} />);
    const image = screen.getByAltText('Лангтанг-трек');
    expect(image).toHaveAttribute('src', '/media/blog/series/langtang.jpg');
  });

  /**
   * Проверяет, что изображение загружается с атрибутом lazy loading.
   * Оптимизация производительности путем отложенной загрузки изображений.
   */
  test('изображение имеет loading="lazy"', () => {
    render(<SeriesCard series={fullSeries} />);
    const image = screen.getByAltText('Лангтанг-трек');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  /**
   * Проверяет, что ссылка на название серии не имеет подчеркивания.
   * В компоненте ссылка на название должна иметь классы text-decoration-none и text-dark.
   */
  test('ссылка на название не имеет подчёркивания', () => {
    const renderResult = render(<SeriesCard series={fullSeries} />);
    const titleLink = renderResult.container.querySelector('.card-title a');
    expect(titleLink).toHaveClass('text-decoration-none', 'text-dark');
  });

  /**
   * Проверяет, что описание является ссылкой.
   * В отличие от CategoryCard, описание в SeriesCard также является ссылкой.
   */
  test('описание является ссылкой', () => {
    render(<SeriesCard series={fullSeries} />);
    const descriptionLink = screen.getByRole('link', { name: 'Поход в Непале' });
    expect(descriptionLink).toBeInTheDocument();
    expect(descriptionLink).toHaveAttribute('href', '/blog/series/langtang-trek/');
  });

  /**
   * Проверяет корректность отображения серии с длинным названием.
   * Компонент должен корректно отображать названия произвольной длины.
   */
  test('рендерит с длинным названием', () => {
    const seriesWithLongName = {
      ...minimalSeries,
      name: 'Очень длинное название серии которое может занимать несколько строк',
    };
    render(<SeriesCard series={seriesWithLongName} />);
    expect(screen.getByText(seriesWithLongName.name)).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения специальных символов в названии.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в названии', () => {
    const seriesWithSpecialChars = {
      ...minimalSeries,
      name: 'Серия <>&"\'',
    };
    render(<SeriesCard series={seriesWithSpecialChars} />);
    expect(screen.getByText(seriesWithSpecialChars.name)).toBeInTheDocument();
  });

  /**
   * Проверяет поведение компонента при пустом URL изображения.
   * При пустом значении image изображение не должно отображаться.
   */
  test('рендерит с пустой строкой в image', () => {
    const seriesWithEmptyImage = {
      ...fullSeries,
      image: '',
    };
    render(<SeriesCard series={seriesWithEmptyImage} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что описание не отображается при его отсутствии.
   */
  test('не отображает описание когда его нет', () => {
    render(<SeriesCard series={minimalSeries} />);
    expect(screen.queryByText(/поход/i)).not.toBeInTheDocument();
  });
});
