import React from 'react';
import { Card } from 'react-bootstrap';
import type { components } from '../../../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Свойства компонента карточки фотографии. */
export interface PhotoCardProps {
  /** Объект фотографии. */
  photo: Photo;
  /** Разрешено ли проявление карточки. */
  revealed?: boolean;
  /** Обработчик загрузки или ошибки загрузки миниатюры. */
  onImageLoad?: () => void;
}

/**
 * Компонент карточки фотографии для отображения в списке/галерее.
 *
 * Простой презентационный компонент, отображающий миниатюру фотографии.
 * Каждая карточка служит кликабельной ссылкой для перехода к детальному
 * просмотру.
 *
 * Прозрачна, пока родительская masonry-сетка не подтвердит проявление
 * (проп revealed): так карточка появляется только на позиции, рассчитанной
 * с учетом ее высоты, и снимки не наваливаются друг на друга в начале
 * загрузки. Карточка без миниатюры видна сразу - ей нечего ждать.
 */
const PhotoCardComponent = ({ photo, revealed = true, onImageLoad }: PhotoCardProps) => {
  const photoUrl = `/gallery/photo/${photo.id}/`;

  return (
    <a href={photoUrl} className="text-decoration-none">
      <Card
        className={`shadow rounded text-center card-entrance ${revealed || !photo.thumbnail_url ? 'is-visible' : ''}`}
      >
        {photo.thumbnail_url && (
          <Card.Img
            className="card-img"
            src={photo.thumbnail_url}
            alt={photo.name}
            loading="lazy"
            onLoad={onImageLoad}
            onError={onImageLoad}
          />
        )}
      </Card>
    </a>
  );
};

export default PhotoCardComponent;
