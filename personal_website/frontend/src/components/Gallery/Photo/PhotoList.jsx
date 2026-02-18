import React, { useState, useEffect } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import PropTypes from 'prop-types';
import PhotoCard from '@components/Gallery/Photo/PhotoCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { Button } from 'react-bootstrap';

/**
 * Компонент списка фотографий галереи.
 *
 * Загружает и отображает список фотографий из API галереи.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
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
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        const data = await response.json();
        const photosList = data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPhotos();
  }, [apiUrl]);

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
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        const data = await response.json();
        const photosList = data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);
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

  // Отображение списка фотографий
  return (
    <Container>
      <Row xs={1} md={4} className="g-4 justify-content-center">
        {photos.map(photo => (
          <Col key={photo.id}>
            <PhotoCard photo={photo} />
          </Col>
        ))}
      </Row>
    </Container>
  );
};

PhotoList.propTypes = {
  apiUrl: PropTypes.string,
};

export default PhotoList;
