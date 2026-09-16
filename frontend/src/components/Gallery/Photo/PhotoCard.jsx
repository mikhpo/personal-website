import React from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент карточки фотографии для отображения в списке/галерее.
 *
 * Это простой презентационный компонент, который отображает миниатюру фотографии.
 * Используется для массового отображения фотографий в сетке галереи.
 * Каждая карточка служит кликабельной ссылкой для перехода к детальному просмотру.
 *
 * Прозрачна, пока родительская masonry-сетка не подтвердит проявление
 * (проп revealed): так карточка появляется только на позиции, рассчитанной
 * с учетом ее высоты, и снимки не наваливаются друг на друга в начале
 * загрузки. Карточка без миниатюры видна сразу - ей нечего ждать.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.photo - Объект фотографии
 * @param {number} props.photo.id - ID фотографии
 * @param {number} props.photo.pk - Первичный ключ фотографии для URL
 * @param {string} props.photo.name - Название фотографии
 * @param {string} [props.photo.thumbnail_url] - URL миниатюры
 * @param {boolean} [props.revealed=true] - Разрешено ли проявление карточки
 * @param {Function} [props.onImageLoad] - Обработчик загрузки или ошибки загрузки миниатюры
 * @return {JSX.Element} Карточка фотографии с миниатюрой
 */
const PhotoCardComponent = ({ photo, revealed = true, onImageLoad }) => {
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

PhotoCardComponent.propTypes = {
  photo: PropTypes.shape({
    id: PropTypes.number.isRequired,
    pk: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    thumbnail_url: PropTypes.string,
  }).isRequired,
  revealed: PropTypes.bool,
  onImageLoad: PropTypes.func,
};

export default PhotoCardComponent;
