import React from 'react';
import PropTypes from 'prop-types';
import ExifData from '@components/Gallery/Photo/ExifData';

/**
 * Компонент с информацией о фотографии для модального окна «О фото».
 *
 * Объединяет ссылку на альбом, описание фотографии и таблицу EXIF данных.
 * Пустые блоки скрываются: без album_name не отображается строка альбома,
 * без description - абзац описания, без EXIF данных не отображается таблица.
 *
 * @component
 * @param {Object} props - Свойства компонента
 * @param {Object} props.photo - Объект фотографии
 * @param {number} [props.photo.album] - ID альбома, в котором размещена фотография
 * @param {string} [props.photo.album_name] - Название альбома (ссылка на страницу альбома)
 * @param {string} [props.photo.description] - Описание фотографии
 * @param {Object} [props.photo] - Остальные поля EXIF данных (см. ExifData)
 * @return {JSX.Element} Блок с информацией о фотографии
 */
const AboutPhoto = ({ photo }) => {
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

AboutPhoto.propTypes = {
  photo: PropTypes.shape({
    album: PropTypes.number,
    album_name: PropTypes.string,
    description: PropTypes.string,
    camera: PropTypes.string,
    lens_model: PropTypes.string,
    aperture: PropTypes.string,
    exposure: PropTypes.string,
    iso: PropTypes.number,
    focal_length: PropTypes.number,
    datetime_taken: PropTypes.string,
  }).isRequired,
};

export default AboutPhoto;
