import React from 'react';
import { Col, Container, Row } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import { useApiData } from '@hooks';

/** Свойства сетки карточек справочника блога. */
export interface TaxonomyGridProps<T extends { id: number }> {
  /** data-testid контейнера для тестов. */
  testId: string;
  /** Заголовок сетки. */
  title: string;
  /** Сообщение индикатора загрузки. */
  loadingMessage: string;
  /** Сообщение пустого списка. */
  emptyMessage: string;
  /** Загружает список элементов, уже отфильтрованный по наличию изображений. */
  fetchFunction: () => Promise<T[]>;
  /** Строит карточку элемента. */
  renderItem: (item: T) => React.ReactNode;
}

/**
 * Сетка карточек справочника блога.
 *
 * Категории и серии используют одинаковую сетку с состояниями загрузки,
 * ошибки и пустого списка; различия передаются пропами.
 *
 * @example
 * <TaxonomyGrid
 *   testId="category-grid-container"
 *   title="Выберите категорию"
 *   loadingMessage="Загрузка категорий..."
 *   emptyMessage="Нет доступных категорий"
 *   fetchFunction={loadCategories}
 *   renderItem={(category) => <CategoryCard category={category} />}
 * />
 */
function TaxonomyGrid<T extends { id: number }>({
  testId,
  title,
  loadingMessage,
  emptyMessage,
  fetchFunction,
  renderItem,
}: TaxonomyGridProps<T>) {
  const { data, loading, error, refetch } = useApiData(fetchFunction);
  const items = data ?? [];

  /** Повторяет загрузку по кнопке "Повторить". */
  const handleRetry = () => {
    refetch();
  };

  if (loading) {
    return <Spinner message={loadingMessage} />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={handleRetry} />;
  }

  if (items.length === 0) {
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  return (
    <Container data-testid={testId}>
      <h2 className="fs-4 text-center">{title}</h2>
      <Row
        xs={1} // 1 колонка на мобильных устройствах
        md={3} // 3 колонки на планшетах и десктопах (>=768px)
        className="g-4 justify-content-center"
      >
        {items.map((item) => (
          <Col key={item.id}>{renderItem(item)}</Col>
        ))}
      </Row>
    </Container>
  );
}

export default TaxonomyGrid;
