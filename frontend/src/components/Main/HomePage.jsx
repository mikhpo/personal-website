import React from 'react';
import CategoryGrid from '@components/Main/CategoryGrid';
import SeriesGrid from '@components/Main/SeriesGrid';

/**
 * Компонент главной страницы сайта.
 *
 * Объединяет сетки категорий и серий блога.
 *
 * @return {JSX.Element} Компонент главной страницы
 *
 * @example
 * // Использование компонента
 * <HomePage />
 *
 * @description
 * Компонент отображает:
 * 1. Сетку категорий блога
 * 2. Отступы между секциями
 * 3. Сетку серий блога
 */
const HomePage = () => {
  return (
    <>
      <CategoryGrid />
      <br />
      <br />
      <SeriesGrid />
      <br />
      <br />
    </>
  );
};

export default HomePage;
