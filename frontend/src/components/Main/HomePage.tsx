import React, { useCallback } from 'react';
import TaxonomyGrid from '@components/Main/TaxonomyGrid';
import CategoryCard from '@components/Main/CategoryCard';
import SeriesCard from '@components/Main/SeriesCard';
import { blogService } from '@services';
import { parseListResponse } from '@utils/pagination';

/**
 * Компонент главной страницы сайта.
 *
 * Объединяет сетки категорий и серий блога: обе строятся общим компонентом
 * TaxonomyGrid с разными справочниками и карточками.
 */
const HomePage = () => {
  const loadCategories = useCallback(async () => {
    const data = await blogService.getCategories();
    const { items } = parseListResponse(data);
    return items.filter((category) => category.image);
  }, []);

  const loadSeries = useCallback(async () => {
    const data = await blogService.getSeries();
    const { items } = parseListResponse(data);
    return items.filter((series) => series.image);
  }, []);

  return (
    <>
      <TaxonomyGrid
        testId="category-grid-container"
        title="Выберите категорию"
        loadingMessage="Загрузка категорий..."
        emptyMessage="Нет доступных категорий"
        fetchFunction={loadCategories}
        renderItem={(category) => <CategoryCard category={category} />}
      />
      <br />
      <br />
      <TaxonomyGrid
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
