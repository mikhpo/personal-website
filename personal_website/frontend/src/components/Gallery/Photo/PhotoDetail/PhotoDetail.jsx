import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import ExifData from '@components/Gallery/Photo/ExifData';
import usePhotoData from '@components/Gallery/Photo/PhotoDetail/hooks/usePhotoData';
import useAlbumPhotos from '@components/Gallery/Photo/PhotoDetail/hooks/useAlbumPhotos';
import usePhotoNavigation from '@components/Gallery/Photo/PhotoDetail/hooks/usePhotoNavigation';

/**
 * Компонент детального просмотра фотографии.
 *
 * Отображает фотографию с кнопками навигации и модальным окном для EXIF данных.
 * Соответствует старой Django реализации.
 *
 * @param {Object} props - Пропсы компонента
 * @param {number} props.photoId - ID фотографии
 * @param {string} [props.apiUrl] - Базовый URL API
 * @return {JSX.Element} Компонент детального просмотра фотографии
 */
const PhotoDetail = ({ photoId, apiUrl = '/api/gallery/photos/' }) => {
  const { photo, loading, error } = usePhotoData(photoId, apiUrl);
  const { photos: albumPhotos } = useAlbumPhotos(photo?.album, '/api/gallery/albums/');
  const { previousPhoto, nextPhoto } = usePhotoNavigation(photo, albumPhotos);
  
  const [showExifModal, setShowExifModal] = useState(false);

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
      <div className="card shadow bg-white rounded justify-content">
        {photo.image_url && (
          <img
            className="card-img"
            src={photo.image_url}
            alt={photo.name}
            style={{ maxHeight: 'calc(100vh - 120px)', width: 'auto', height: 'auto', maxWidth: '100%' }}
          />
        )}
        <div className="card-footer" align="center">
          <div className="btn-group" role="group" aria-label="Photo navigation buttons">
            {previousPhoto && (
              <a
                href={`/gallery/photo/${previousPhoto.id}/`}
                className="btn btn-outline-dark"
                id="previous-photo-link"
              >
                {"<"}
              </a>
            )}
            <Button
              variant="outline-dark"
              onClick={() => setShowExifModal(true)}
            >
              О фото
            </Button>
            {nextPhoto && (
              <a
                href={`/gallery/photo/${nextPhoto.id}/`}
                className="btn btn-outline-dark"
                id="next-photo-link"
              >
                {">"}
              </a>
            )}
          </div>
        </div>
      </div>

      <Modal show={showExifModal} onHide={() => setShowExifModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title id="exifModalLabel">EXIF</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ExifData photo={photo} />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-dark" onClick={() => setShowExifModal(false)}>
            Закрыть
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

PhotoDetail.propTypes = {
  photoId: PropTypes.number.isRequired,
  apiUrl: PropTypes.string,
};

export default PhotoDetail;