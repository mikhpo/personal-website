import React, { useCallback, useEffect, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import CategoryCard from '@components/Main/CategoryCard';
import { blogService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../types/api-schema';

type Category = components['schemas']['Category'];

/**
 * Компонент сетки категорий блога.
 *
 * Загружает список категорий через сервис API, фильтрует категории
 * с изображениями и отображает их сеткой карточек, обрабатывая состояния
 * загрузки, ошибки и пустого списка с возможностью повторной загрузки
 * при ошибке.
 */
const CategoryGrid = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCategories = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await blogService.getCategories();
      const { items } = parseListResponse(data);
      const withImages = items.filter((cat) => cat.image);
      setCategories(withImages);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  const handleRetry = () => {
    loadCategories();
  };

  if (loading) {
    return <Spinner message="Загрузка категорий..." />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={handleRetry} />;
  }

  if (categories.length === 0) {
    return <AlertList messages={[{ message: 'Нет доступных категорий', level: 'info' }]} />;
  }

  return (
    <Container data-testid="category-grid-container">
      <h2 className="fs-4 text-center">Выберите категорию</h2>
      <Row
        xs={1} // 1 колонка на мобильных устройствах
        md={3} // 3 колонки на планшетах и десктопах (>=768px)
        className="g-4 justify-content-center"
      >
        {categories.map((category) => (
          <Col key={category.id}>
            <CategoryCard category={category} />
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default CategoryGrid;
