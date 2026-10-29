import React, { useCallback } from 'react';
import CardGrid from '@components/Main/CardGrid';
import CategoryCard from '@components/Main/CategoryCard';
import SeriesCard from '@components/Main/SeriesCard';
import { blogService } from '@services';

/**
 * Компонент главной страницы сайта.
 *
 * Объединяет сетки категорий и серий блога: обе строятся общим компонентом
 * CardGrid с разными справочниками и карточками.
 */
const HomePage = () => {
  const loadCategories = useCallback(async () => {
    const categories = await blogService.getCategories();
    return categories.filter((category) => category.image);
  }, []);

  const loadSeries = useCallback(async () => {
    const series = await blogService.getSeries();
    return series.filter((series) => series.image);
  }, []);

  return (
    <>
      <CardGrid
        testId="category-grid-container"
        title="Выберите категорию"
        loadingMessage="Загрузка категорий..."
        emptyMessage="Нет доступных категорий"
        fetchFunction={loadCategories}
        renderItem={(category) => <CategoryCard category={category} />}
      />
      <br />
      <br />
      <CardGrid
        testId="series-grid-container"
        title="Или серию"
        loadingMessage="Загрузка серий..."
        emptyMessage="Нет доступных серий"
        fetchFunction={loadSeries}
        renderItem={(series) => <SeriesCard series={series} />}
      />
      <br />
      <br />
    </>
  );
};

export default HomePage;
