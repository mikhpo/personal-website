import React from 'react';
import PropTypes from 'prop-types';
import BaseCard from '@components/Card/BaseCard';

/**
 * Компонент карточки альбома.
 *
 * Отображает превью альбома с обложкой, названием и описанием.
 * Прозрачна, пока родительская masonry-сетка не подтвердит проявление
 * (проп revealed); альбом без обложки виден сразу - его высота известна
 * без загрузки изображения.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.album - Объект альбома
 * @param {number} props.album.id - ID альбома (первичный ключ)
 * @param {string} props.album.name - Название альбома
 * @param {string} [props.album.description] - Описание альбома
 * @param {string} [props.album.cover_thumbnail_url] - URL миниатюры обложки
 * @param {boolean} [props.revealed=true] - Разрешено ли проявление карточки
 * @param {Function} [props.onImageLoad] - Обработчик загрузки или ошибки загрузки
 *   обложки; вызывается с id альбома
 * @return {JSX.Element} Компонент карточки альбома
 */
const AlbumCard = ({ album, revealed = true, onImageLoad }) => {
  const albumUrl = `/gallery/album/${album.id}/`;
  const handleImageReady = () => {
    if (onImageLoad) {
      onImageLoad(album.id);
    }
  };

  // Если есть обложка, используем BaseCard
  if (album.cover_thumbnail_url) {
    return (
      <BaseCard
        title={album.name}
        url={albumUrl}
        image={album.cover_thumbnail_url}
        description={album.description}
        imageAlt={album.name}
        revealed={revealed}
        cardImgProps={{ onLoad: handleImageReady, onError: handleImageReady }}
      />
    );
  }

  // Если обложки нет, отображаем плейсхолдер
  return (
    <div className="card shadow rounded text-center h-100">
      <div
        className="card-img-top bg-body-tertiary d-flex align-items-center justify-content-center"
        style={{ height: '200px' }}
      >
        <span className="text-muted">Нет обложки</span>
      </div>
      <div className="card-body d-flex flex-column">
        <h3 className="card-title mt-auto fs-5">
          <a href={albumUrl} className="text-decoration-none text-body">
            {album.name}
          </a>
        </h3>
        {album.description && <p className="card-text">{album.description}</p>}
      </div>
    </div>
  );
};

AlbumCard.propTypes = {
  album: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    cover_thumbnail_url: PropTypes.string,
  }).isRequired,
  revealed: PropTypes.bool,
  onImageLoad: PropTypes.func,
};

export default AlbumCard;
