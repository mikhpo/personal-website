import React, { useState, useEffect } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import PropTypes from 'prop-types';
import PhotoCard from '@components/Gallery/Photo/PhotoCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { Button } from 'react-bootstrap';
import Pagination from '@components/Pagination/Pagination';

/**
 * Компонент списка фотографий галереи.
 *
 * Загружает и отображает список фотографий из API галереи.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
 * Поддерживает пагинацию для навигации по большому количеству фотографий.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.apiUrl="/api/gallery/photos/"] - URL API для загрузки фотографий
 * @return {JSX.Element} Компонент списка фотографий
 *
 * @example
 * // Использование с URL по умолчанию
 * <PhotoList />
 *
 * @example
 * // Использование с пользовательским URL
 * <PhotoList apiUrl="/api/gallery/album/1/photos/" />
 */
const PhotoList = ({ apiUrl = '/api/gallery/photos/' }) => {
  /**
   * Состояние фотографий
   * @type {[Array, function]}
   */
  const [photos, setPhotos] = useState([]);

  /**
   * Состояние загрузки данных
   * @type {[boolean, function]}
   */
  const [loading, setLoading] = useState(true);

  /**
   * Состояние ошибки при загрузке данных
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

  /**
   * Состояние данных пагинации
   * @type {[Object, function]}
   */
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    totalPages: 0,
  });

  /**
   * Загрузить данные по указанному URL
   * @async
   * @function fetchUrl
   * @param {string} url - URL для запроса
   * @return {Promise<Object>} Данные из API
   */
  const fetchUrl = async (url) => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }
    return await response.json();
  };

  /**
   * Эффект для загрузки фотографий при монтировании компонента или изменении apiUrl
   * Выполняет запрос к API и обновляет состояние компонента
   */
  useEffect(() => {
    /**
     * Асинхронная функция для загрузки фотографий из API
     * @async
     * @function loadPhotos
     * @return {Promise<void>}
     */
    const loadPhotos = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(apiUrl);
        const photosList = data.photos || data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);

        // Обновить данные пагинации
        const totalPages = data.count ? Math.ceil(data.count / photosList.length) : 0;
        setPagination({
          count: data.count || 0,
          next: data.next,
          previous: data.previous,
          currentPage: 1,
          totalPages: totalPages,
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPhotos();
  }, [apiUrl]);

  /**
   * Обработчик изменения страницы пагинации
   * @async
   * @function handlePageChange
   * @param {number} page - Номер страницы для перехода
   * @return {Promise<void>}
   */
  const handlePageChange = async (page) => {
    if (page < 1 || !pagination.totalPages || page > pagination.totalPages) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Построить URL с параметром страницы
      const url = new URL(apiUrl, window.location.origin);
      url.searchParams.set('page', page);

      const data = await fetchUrl(url.toString());
      const photosList = data.results || data;
      setPhotos(Array.isArray(photosList) ? photosList : []);

      // Обновить данные пагинации
      setPagination({
        count: data.count || 0,
        next: data.next,
        previous: data.previous,
        currentPage: page,
        totalPages: pagination.totalPages,
      });

      // Прокрутить страницу вверх
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Обработчик перехода на следующую страницу
   * @async
   * @function handleNext
   * @return {Promise<void>}
   */
  const handleNext = async () => {
    if (pagination.next) {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(pagination.next);
        const photosList = data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);

        // Вычислить текущую страницу из URL
        const url = new URL(pagination.next);
        const page = parseInt(url.searchParams.get('page') || '1', 10);

        setPagination({
          count: data.count || 0,
          next: data.next,
          previous: data.previous,
          currentPage: page,
          totalPages: pagination.totalPages,
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  /**
   * Обработчик перехода на предыдущую страницу
   * @async
   * @function handlePrevious
   * @return {Promise<void>}
   */
  const handlePrevious = async () => {
    if (pagination.previous) {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(pagination.previous);
        const photosList = data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);

        // Вычислить текущую страницу из URL
        const url = new URL(pagination.previous);
        const page = parseInt(url.searchParams.get('page') || '1', 10);

        setPagination({
          count: data.count || 0,
          next: data.next,
          previous: data.previous,
          currentPage: page,
          totalPages: pagination.totalPages,
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  /**
   * Обработчик повторной попытки загрузки данных
   * Сбрасывает состояние ошибки и повторно выполняет запрос к API
   * @function handleRetry
   * @return {void}
   */
  const handleRetry = () => {
    /**
     * Асинхронная функция для повторной загрузки фотографий из API
     * @async
     * @function retryLoadPhotos
     * @return {Promise<void>}
     */
    const retryLoadPhotos = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(apiUrl);
        const photosList = data.photos || data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);

        const totalPages = data.count ? Math.ceil(data.count / photosList.length) : 0;
        setPagination({
          count: data.count || 0,
          next: data.next,
          previous: data.previous,
          currentPage: 1,
          totalPages: totalPages,
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    retryLoadPhotos();
  };

  // Отображение индикатора загрузки
  if (loading) {
    return <SpinnerComponent message="Загрузка фотографий..." />;
  }

  // Отображение сообщения об ошибке с кнопкой повтора
  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: 'error',
            actions: (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={handleRetry}
              >
                Повторить
              </Button>
            )
          }
        ]}
      />
    );
  }

  // Отображение сообщения о пустом списке фотографий
  if (photos.length === 0) {
    return <AlertList messages={[{ message: "Нет доступных фотографий", level: "info" }]} />;
  }

  // Отображение списка фотографий с пагинацией
  return (
    <Container>
      <Row xs={1} md={4} className="g-4 justify-content-center">
        {photos.map(photo => (
          <Col key={photo.id}>
            <PhotoCard photo={photo} />
          </Col>
        ))}
      </Row>
      <Pagination
        currentPage={pagination.currentPage}
        totalPages={pagination.totalPages}
        hasNext={!!pagination.next}
        hasPrevious={!!pagination.previous}
        onPageChange={handlePageChange}
        onNext={handleNext}
        onPrevious={handlePrevious}
      />
    </Container>
  );
};

PhotoList.propTypes = {
  apiUrl: PropTypes.string,
};

export default PhotoList;
