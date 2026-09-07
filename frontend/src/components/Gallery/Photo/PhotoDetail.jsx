import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import AboutPhoto from '@components/Gallery/Photo/AboutPhoto';
import { usePhotoData, usePhotoNavigation } from '@hooks';

/**
 * Компонент детального просмотра фотографии.
 *
 * Отображает фотографию с кнопками навигации и модальным окном
 * с информацией о фотографии (альбом, описание, EXIF данные).
 * Соответствует старой Django реализации.
 * Поддерживает переключение фотографий клавишами ArrowLeft/ArrowRight
 * и горизонтальными свайпами на сенсорных экранах (см. usePhotoNavigation);
 * при открытом модальном окне навигация отключена.
 *
 * @param {Object} props - Пропсы компонента
 * @param {number} props.photoId - ID фотографии
 * @param {number} [props.previousPhotoId] - ID предыдущей фотографии (опционально)
 * @param {number} [props.nextPhotoId] - ID следующей фотографии (опционально)
 * @param {string} [props.apiUrl] - Базовый URL API
 * @return {JSX.Element} Компонент детального просмотра фотографии
 */
const PhotoDetail = ({ photoId, previousPhotoId, nextPhotoId, apiUrl = '/api/gallery/photos/' }) => {
  const { photo, loading, error } = usePhotoData(photoId, apiUrl);

  const [showAboutModal, setShowAboutModal] = useState(false);

  const previousUrl = previousPhotoId ? `/gallery/photo/${previousPhotoId}/` : null;
  const nextUrl = nextPhotoId ? `/gallery/photo/${nextPhotoId}/` : null;

  usePhotoNavigation({
    previousUrl,
    nextUrl,
    enabled: !showAboutModal,
  });

  if (loading) {
    return <div className="container mt-3">Загрузка фотографии...</div>;
  }

  if (error) {
    return (
      <div className="container mt-3">
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </div>
    );
  }

  if (!photo) {
    return (
      <div className="container mt-3">
        <div className="alert alert-danger" role="alert">
          Фотография не найдена
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ overflowY: 'auto', maxHeight: '100vh' }}>
      <div className="card shadow rounded justify-content">
        {photo.image_url && (
          <img
            className="card-img"
            src={photo.image_url}
            alt={photo.name}
            style={{ maxWidth: '100%', maxHeight: 'calc(100vh - 120px)', objectFit: 'contain' }}
          />
        )}
        <div className="card-footer" align="center">
          <div className="btn-group" role="group" aria-label="Навигация по фотографиям">
            {previousUrl && (
              <a
                href={previousUrl}
                className="btn btn-outline-dark"
                id="previous-photo-link"
                aria-label="Предыдущая фотография"
              >
                {"<"}
              </a>
            )}
            <Button
              variant="outline-dark"
              onClick={() => setShowAboutModal(true)}
            >
              О фото
            </Button>
            {nextUrl && (
              <a
                href={nextUrl}
                className="btn btn-outline-dark"
                id="next-photo-link"
                aria-label="Следующая фотография"
              >
                {">"}
              </a>
            )}
          </div>
        </div>
      </div>

      <Modal
        show={showAboutModal}
        onHide={() => setShowAboutModal(false)}
        aria-labelledby="aboutPhotoModalLabel"
      >
        <Modal.Header closeButton>
          <Modal.Title id="aboutPhotoModalLabel">О фото</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <AboutPhoto photo={photo} />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-dark" onClick={() => setShowAboutModal(false)}>
            Закрыть
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

PhotoDetail.propTypes = {
  photoId: PropTypes.number.isRequired,
  previousPhotoId: PropTypes.number,
  nextPhotoId: PropTypes.number,
  apiUrl: PropTypes.string,
};

export default PhotoDetail;
