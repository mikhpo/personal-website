import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import AboutPhoto from '@components/Gallery/Photo/AboutPhoto';
import EmbedLinksModal from '@components/Gallery/Photo/EmbedLinksModal';
import PhotoNavigation from '@components/Gallery/Photo/PhotoNavigation';
import { usePhotoData, usePhotoNavigation } from '@hooks';

/** Свойства компонента детального просмотра фотографии. */
export interface PhotoDetailProps {
  /** ID фотографии. */
  photoId: number;
  /** Признак staff: показывать кнопку получения ссылок. */
  isStaff?: boolean;
  /** Размеры превью для вставок в пикселах по наибольшей стороне. */
  embedSizes?: number[];
}

/**
 * Компонент детального просмотра фотографии.
 *
 * Отображает превью фотографии с кнопками навигации и модальным окном
 * с информацией о фотографии (альбом, описание, EXIF данные).
 * Превью генерируется сервером при первом обращении, поэтому
 * страница всегда загружает облегченный вариант изображения.
 * Поддерживает переключение фотографий клавишами ArrowLeft/ArrowRight
 * и горизонтальными свайпами на сенсорных экранах (см. usePhotoNavigation);
 * при открытом модальном окне навигация отключена.
 * Для staff доступна кнопка получения постоянных ссылок на превью
 * фотографии для вставки в статьи.
 * Фотография проявляется плавно после загрузки; клик по ней открывает
 * оригинал в новой вкладке.
 */
const PhotoDetail = ({ photoId, isStaff = false, embedSizes = [] }: PhotoDetailProps) => {
  const { photo, loading, error } = usePhotoData(photoId);

  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showEmbedModal, setShowEmbedModal] = useState(false);

  // Готовность хранится с привязкой к id: при переключении фотографии
  // новая проявляется заново, без сброса состояния в эффекте
  const [loadedPhotoId, setLoadedPhotoId] = useState<number | null>(null);
  const imageReady = loadedPhotoId === photoId;

  // Соседи приходят полями previous_id/next_id детального ответа API
  const previousUrl = photo?.previous_id ? `/gallery/photo/${photo.previous_id}/` : null;
  const nextUrl = photo?.next_id ? `/gallery/photo/${photo.next_id}/` : null;

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

  // Превью генерируется сервером при первом обращении, поэтому
  // откат к оригиналу не нужен: страница всегда грузит облегченный вариант
  return (
    <div className="container" style={{ overflowY: 'auto', maxHeight: '100vh' }}>
      <div className="card shadow rounded justify-content">
        {photo.preview_url && (
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
              src={photo.preview_url}
              alt={photo.name}
              style={{ maxWidth: '100%', maxHeight: 'calc(100vh - 120px)', objectFit: 'contain' }}
              onLoad={() => setLoadedPhotoId(photoId)}
              onError={() => setLoadedPhotoId(photoId)}
            />
          </a>
        )}
        {/* align - устаревший HTML-атрибут; приведение сохраняет прежний DOM */}
        {/* align - устаревший HTML-атрибут; приведение сохраняет прежний DOM */}
        <div className="card-footer" {...({ align: 'center' } as React.HTMLAttributes<HTMLDivElement>)}>
          <div className="btn-group" role="group" aria-label="Навигация по фотографиям">
            <PhotoNavigation previousUrl={previousUrl} nextUrl={nextUrl}>
              <Button variant="outline-dark" onClick={() => setShowAboutModal(true)}>
                О фото
              </Button>
              {isStaff && (
                <Button variant="outline-dark" id="get-embed-link-button" onClick={() => setShowEmbedModal(true)}>
                  Ссылка для вставки
                </Button>
              )}
            </PhotoNavigation>
          </div>
        </div>
      </div>

      <Modal show={showAboutModal} onHide={() => setShowAboutModal(false)} aria-labelledby="aboutPhotoModalLabel">
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
        <Modal show={showEmbedModal} onHide={() => setShowEmbedModal(false)} aria-labelledby="embedLinksModalLabel">
          <Modal.Header closeButton>
            <Modal.Title id="embedLinksModalLabel">Ссылка для вставки</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <EmbedLinksModal
              photoId={photoId}
              sizes={embedSizes}
              ext={photo.image_url ? (photo.image_url.split('.').pop()?.toLowerCase() ?? 'jpg') : 'jpg'}
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

export default PhotoDetail;
