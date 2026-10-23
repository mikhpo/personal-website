import React from 'react';
import CategoryGrid from '@components/Main/CategoryGrid';
import SeriesGrid from '@components/Main/SeriesGrid';

/**
 * Компонент главной страницы сайта.
 *
 * Объединяет сетки категорий и серий блога.
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
