import React, { useCallback, useEffect, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import SeriesCard from '@components/Main/SeriesCard';
import { blogService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../types/api-schema';

type Series = components['schemas']['Series'];

/**
 * Компонент сетки серий блога.
 *
 * Загружает список серий через сервис API, фильтрует серии с изображениями
 * и отображает их сеткой карточек, обрабатывая состояния загрузки, ошибки
 * и пустого списка с возможностью повторной загрузки при ошибке.
 */
const SeriesGrid = () => {
  const [series, setSeries] = useState<Series[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSeries = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await blogService.getSeries();
      const { items } = parseListResponse(data);
      const withImages = items.filter((s) => s.image);
      setSeries(withImages);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, []);

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
