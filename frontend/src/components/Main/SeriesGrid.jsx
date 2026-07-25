import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import SeriesCard from '@components/Main/SeriesCard';

/**
 * Компонент сетки серий блога.
 *
 * Загружает и отображает список серий из API. Обрабатывает различные состояния:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 *
 * @return {JSX.Element} Компонент сетки серий
 *
 * @example
 * // Использование компонента
 * <SeriesGrid />
 *
 * @description
 * Компонент выполняет следующие функции:
 * 1. Загружает данные серий через fetch API
 * 2. Фильтрует серии с изображениями
 * 3. Обрабатывает состояния загрузки, ошибки и пустого списка
 * 4. Отображает серии в виде сетки карточек
 * 5. Предоставляет возможность повторной загрузки при ошибке
 */

// URL для получения списка серий
const SERIES_API_URL = '/api/blog/series/';

const SeriesGrid = () => {
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSeriesRequest = useCallback(async () => {
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
      const seriesList = data.results || data;
      const withImages = (Array.isArray(seriesList) ? seriesList : [])
        .filter((s) => s.image);
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
    return (
      <AlertList
        messages={[{ message: 'Нет доступных серий', level: 'info' }]}
      />
    );
  }

  return (
    <Container data-testid="series-grid-container">
      <h4>
        <p className="text-center">Или серию</p>
      </h4>
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
