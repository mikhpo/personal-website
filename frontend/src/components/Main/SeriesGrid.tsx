import React, { useCallback, useEffect, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import SeriesCard from '@components/Main/SeriesCard';
import type { components } from '../../types/api-schema';
import type { Paginated } from '../../types/pagination';

type Series = components['schemas']['Series'];

// URL для получения списка серий
const SERIES_API_URL = '/api/blog/series/';

/**
 * Компонент сетки серий блога.
 *
 * Загружает список серий из API, фильтрует серии с изображениями
 * и отображает их сеткой карточек, обрабатывая состояния загрузки, ошибки
 * и пустого списка с возможностью повторной загрузки при ошибке.
 */
const SeriesGrid = () => {
  const [series, setSeries] = useState<Series[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSeriesRequest = useCallback(async (): Promise<Paginated<Series> | Series[]> => {
    const response = await fetch(SERIES_API_URL);

    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }

    return response.json();
  }, []);

  // useCallback обеспечивает стабильность ссылки для useEffect и handleRetry
  const loadSeries = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchSeriesRequest();
      // До нормализации (фаза 6) конверт читается как объединение: массив или конверт
      const raw = Array.isArray(data) ? data : data.results || data;
      const seriesList = Array.isArray(raw) ? raw : [];
      const withImages = seriesList.filter((s) => s.image);
      setSeries(withImages);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, [fetchSeriesRequest]);

  useEffect(() => {
    loadSeries();
  }, [loadSeries]);

  const handleRetry = () => {
    loadSeries();
  };

  if (loading) {
    return <Spinner message="Загрузка серий..." />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={handleRetry} />;
  }

  if (series.length === 0) {
    return <AlertList messages={[{ message: 'Нет доступных серий', level: 'info' }]} />;
  }

  return (
    <Container data-testid="series-grid-container">
      <h2 className="fs-4 text-center">Или серию</h2>
      <Row
        xs={1} // 1 колонка на мобильных устройствах
        md={3} // 3 колонки на планшетах и десктопах (>=768px)
        className="g-4 justify-content-center"
      >
        {series.map((s) => (
          <Col key={s.id}>
            <SeriesCard series={s} />
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default SeriesGrid;
