import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import AboutPhoto from '@components/Gallery/Photo/AboutPhoto';
import EmbedLinksModal from '@components/Gallery/Photo/EmbedLinksModal';
import { usePhotoData, usePhotoNavigation } from '@hooks';

/**
 * Компонент детального просмотра фотографии.
 *
 * Отображает превью фотографии с кнопками навигации и модальным окном
 * с информацией о фотографии (альбом, описание, EXIF данные).
 * Соответствует старой Django реализации.
 * Поддерживает переключение фотографий клавишами ArrowLeft/ArrowRight
 * и горизонтальными свайпами на сенсорных экранах (см. usePhotoNavigation);
 * при открытом модальном окне навигация отключена.
 * Для staff доступна кнопка получения постоянных ссылок
 * на превью фотографии для вставки в статьи.
 * Фотография проявляется плавно после загрузки; клик по ней открывает
 * оригинал в новой вкладке.
 *
 * @param {Object} props - Пропсы компонента
 * @param {number} props.photoId - ID фотографии
 * @param {number} [props.previousPhotoId] - ID предыдущей фотографии (опционально)
 * @param {number} [props.nextPhotoId] - ID следующей фотографии (опционально)
 * @param {boolean} [props.isStaff] - Признак staff: показывать кнопку получения ссылок
 * @param {number[]} [props.embedSizes] - Размеры превью для вставок в пикселах по наибольшей стороне
 * @param {string} [props.apiUrl] - Базовый URL API
 * @return {JSX.Element} Компонент детального просмотра фотографии
 */
const PhotoDetail = ({
  photoId,
  previousPhotoId,
  nextPhotoId,
  isStaff = false,
  embedSizes = [],
  apiUrl = '/api/gallery/photos/',
}) => {
  const { photo, loading, error } = usePhotoData(photoId, apiUrl);

  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showEmbedModal, setShowEmbedModal] = useState(false);

  // Готовность хранится с привязкой к id: при переключении фотографии
  // новая проявляется заново, без сброса состояния в эффекте
  const [loadedPhotoId, setLoadedPhotoId] = useState(null);
  const imageReady = loadedPhotoId === photoId;

  const previousUrl = previousPhotoId ? `/gallery/photo/${previousPhotoId}/` : null;
  const nextUrl = nextPhotoId ? `/gallery/photo/${nextPhotoId}/` : null;

  usePhotoNavigation({
    previousUrl,
    nextUrl,
    enabled: !showAboutModal && !showEmbedModal,
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

  const displayUrl = photo.preview_url || photo.image_url;

  return (
    <div className="container" style={{ overflowY: 'auto', maxHeight: '100vh' }}>
      <div className="card shadow rounded justify-content">
        {displayUrl && (
          <a
            href={photo.image_url}
            target="_blank"
            rel="noopener noreferrer"
            title="Открыть оригинал"
            aria-label="Открыть оригинал"
            className={`card-entrance ${imageReady ? 'is-visible' : ''}`}
          >
            <img
              className="card-img"
              src={displayUrl}
              alt={photo.name}
              style={{ maxWidth: '100%', maxHeight: 'calc(100vh - 120px)', objectFit: 'contain' }}
              onLoad={() => setLoadedPhotoId(photoId)}
              onError={() => setLoadedPhotoId(photoId)}
            />
          </a>
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
            {isStaff && (
              <Button
                variant="outline-dark"
                id="get-embed-link-button"
                onClick={() => setShowEmbedModal(true)}
              >
                Ссылка для вставки
              </Button>
            )}
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

      {isStaff && (
        <Modal
          show={showEmbedModal}
          onHide={() => setShowEmbedModal(false)}
          aria-labelledby="embedLinksModalLabel"
        >
          <Modal.Header closeButton>
            <Modal.Title id="embedLinksModalLabel">Ссылка для вставки</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <EmbedLinksModal
              photoId={photoId}
              sizes={embedSizes}
              ext={photo.image_url ? photo.image_url.split('.').pop().toLowerCase() : 'jpg'}
            />
          </Modal.Body>
          <Modal.Footer>
            <Button variant="outline-dark" onClick={() => setShowEmbedModal(false)}>
              Закрыть
            </Button>
          </Modal.Footer>
        </Modal>
      )}
    </div>
  );
};

PhotoDetail.propTypes = {
  photoId: PropTypes.number.isRequired,
  previousPhotoId: PropTypes.number,
  nextPhotoId: PropTypes.number,
  isStaff: PropTypes.bool,
  embedSizes: PropTypes.arrayOf(PropTypes.number),
  apiUrl: PropTypes.string,
};

export default PhotoDetail;
