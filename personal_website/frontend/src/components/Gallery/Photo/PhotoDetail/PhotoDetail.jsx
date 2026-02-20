import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import PropTypes from 'prop-types';
import ExifData from '@components/Gallery/Photo/ExifData';
import PhotoTags from '@components/Gallery/Photo/PhotoTags';
import PhotoNavigation from '@components/Gallery/Photo/PhotoNavigation';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import usePhotoData from '@components/Gallery/Photo/PhotoDetail/hooks/usePhotoData';
import useAlbumPhotos from '@components/Gallery/Photo/PhotoDetail/hooks/useAlbumPhotos';
import usePhotoNavigation from '@components/Gallery/Photo/PhotoDetail/hooks/usePhotoNavigation';

/**
 * Компонент детального просмотра фотографии (альтернативная реализация).
 *
 * Это сложный компонент с бизнес-логикой, который загружает данные фотографии 
 * через API и отображает полную информацию о ней. Включает навигацию между 
 * фотографиями в альбоме, отображение EXIF-данных, тегов и описания.
 * Используется для отдельной страницы детального просмотра конкретной фотографии.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} props.photoSlug - Слаг фотографии
 * @param {string} [props.apiUrl] - Базовый URL API (опционально, по умолчанию /api/gallery/photos/)
 * @return {JSX.Element} Компонент детального просмотра фотографии
 */
const PhotoDetail = ({ photoSlug, apiUrl = '/api/gallery/photos/' }) => {
  // Используем хуки для загрузки данных
  const { photo, loading, error, refetch: refetchPhoto } = usePhotoData(photoSlug, apiUrl);
  const { photos: albumPhotos, refetch: refetchAlbumPhotos } = useAlbumPhotos(photo?.album, apiUrl);
  
  // Используем хук для вычисления навигации
  const { previousPhoto, nextPhoto } = usePhotoNavigation(photo, albumPhotos);

  const handleRetry = () => {
    refetchPhoto();
    if (photo?.album) {
      refetchAlbumPhotos();
    }
  };

  if (loading) {
    return <SpinnerComponent message="Загрузка фотографии..." />;
  }

  if (error) {
    return (
      <div className="container mt-3">
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <div>
            {error}
            <button className="btn btn-sm btn-primary ms-2" onClick={handleRetry}>
              Повторить
            </button>
          </div>
          <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      </div>
    );
  }

  if (!photo) {
    return <AlertList messages={[{ message: "Фотография не найдена", level: 'error' }]} />;
  }

  return (
    <Container className="my-4">
      <Row>
        <Col md={8}>
          <Card className="shadow-sm">
            {photo.image_url && (
              <Card.Img
                variant="top"
                src={photo.image_url}
                alt={photo.name}
                loading="lazy"
              />
            )}
          </Card>
          <PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />
        </Col>
        <Col md={4}>
          <Card className="shadow-sm mb-3">
            <Card.Body>
              <Card.Title>{photo.name}</Card.Title>
              {photo.description && <Card.Text>{photo.description}</Card.Text>}
            </Card.Body>
          </Card>

          {photo.tags && photo.tags.length > 0 && (
            <Card className="shadow-sm mb-3">
              <Card.Body>
                <PhotoTags tags={photo.tags} />
              </Card.Body>
            </Card>
          )}

          <Card className="shadow-sm">
            <Card.Body>
              <h6 className="fw-bold mb-3">Информация</h6>
              <ExifData photo={photo} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

PhotoDetail.propTypes = {
  photoSlug: PropTypes.string.isRequired,
  apiUrl: PropTypes.string,
};

export default PhotoDetail;
