import React from 'react';
import ExifData from '@components/Gallery/Photo/ExifData';
import type { components } from '../../../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Свойства компонента информации о фотографии. */
export interface AboutPhotoProps {
  /** Объект фотографии. */
  photo: Photo;
}

/**
 * Компонент с информацией о фотографии для модального окна "О фото".
 *
 * Объединяет ссылку на альбом, описание фотографии и таблицу EXIF данных.
 * Пустые блоки скрываются: без album_name не отображается строка альбома,
 * без description - абзац описания, без EXIF данных не отображается таблица.
 */
const AboutPhoto = ({ photo }: AboutPhotoProps) => {
  return (
    <>
      {photo.album_name && (
        <p className="mb-2">
          Альбом: <a href={`/gallery/album/${photo.album}/`}>{photo.album_name}</a>
        </p>
      )}
      {photo.description && <p className="mb-2">{photo.description}</p>}
      <ExifData photo={photo} />
    </>
  );
};

export default AboutPhoto;
