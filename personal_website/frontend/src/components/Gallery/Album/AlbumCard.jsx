import React from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент карточки альбома.
 *
 * Отображает превью альбома с обложкой, названием и описанием.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.album - Объект альбома
 * @param {number} props.album.id - ID альбома
 * @param {string} props.album.name - Название альбома
 * @param {string} props.album.slug - Слаг альбома для URL
 * @param {string} [props.album.description] - Описание альбома
 * @param {string} [props.album.cover_thumbnail_url] - URL миниатюры обложки
 * @return {JSX.Element} Компонент карточки альбома
 */
const AlbumCard = ({ album }) => {
  const albumUrl = `/gallery/album/${album.slug}/`;

  return (
    <Card className="shadow bg-white rounded text-center h-100">
      {album.cover_thumbnail_url && (
        <a href={albumUrl}>
          <Card.Img
            variant="top"
            src={album.cover_thumbnail_url}
            alt={album.name}
            loading="lazy"
          />
        </a>
      )}
      {!album.cover_thumbnail_url && (
        <div
          className="card-img-top bg-light d-flex align-items-center justify-content-center"
          style={{ height: '200px' }}
        >
          <span className="text-muted">Нет обложки</span>
        </div>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title className="mt-auto">
          <a href={albumUrl} className="text-decoration-none text-dark">
            {album.name}
          </a>
        </Card.Title>
      </Card.Body>
    </Card>
  );
};

AlbumCard.propTypes = {
  album: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    description: PropTypes.string,
    cover_thumbnail_url: PropTypes.string,
  }).isRequired,
};

export default AlbumCard;
