import React from 'react';
import PropTypes from 'prop-types';
import BaseCard from '@components/Card/BaseCard';

/**
 * Компонент карточки альбома.
 *
 * Отображает превью альбома с обложкой, названием и описанием.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.album - Объект альбома
 * @param {number} props.album.id - ID альбома (первичный ключ)
 * @param {string} props.album.name - Название альбома
 * @param {string} [props.album.description] - Описание альбома
 * @param {string} [props.album.cover_thumbnail_url] - URL миниатюры обложки
 * @return {JSX.Element} Компонент карточки альбома
 */
const AlbumCard = ({ album }) => {
  const albumUrl = `/gallery/album/${album.id}/`;

  // Если есть обложка, используем BaseCard
  if (album.cover_thumbnail_url) {
    return (
      <BaseCard
        title={album.name}
        url={albumUrl}
        image={album.cover_thumbnail_url}
        description={album.description}
        imageAlt={album.name}
      />
    );
  }

  // Если обложки нет, отображаем плейсхолдер
  return (
    <div className="card shadow bg-white rounded text-center h-100">
      <div
        className="card-img-top bg-light d-flex align-items-center justify-content-center"
        style={{ height: '200px' }}
      >
        <span className="text-muted">Нет обложки</span>
      </div>
      <div className="card-body d-flex flex-column">
        <h3 className="card-title mt-auto fs-5">
          <a href={albumUrl} className="text-dark">
            {album.name}
          </a>
        </h3>
        {album.description && (
          <p className="card-text">{album.description}</p>
        )}
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
};

export default AlbumCard;
