import React from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент карточки фотографии.
 *
 * Отображает превью фотографии с названием и датой съёмки.
 * Создает кликабельную карточку с миниатюрой фотографии, названием и датой съёмки.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.photo - Объект фотографии
 * @param {number} props.photo.id - ID фотографии
 * @param {string} props.photo.name - Название фотографии
 * @param {string} props.photo.slug - Слаг фотографии для URL
 * @param {string} [props.photo.thumbnail_url] - URL миниатюры
 * @param {string} [props.photo.datetime_taken] - Дата и время съёмки (ISO формат)
 * @return {JSX.Element} Карточка фотографии с миниатюрой, названием и датой
 *
 * @example
 * // Пример использования компонента
 * const photoData = {
 *   id: 1,
 *   name: "Закат над озером",
 *   slug: "zakat-nad-ozerom",
 *   thumbnail_url: "/media/photos/thumb_zakat.jpg",
 *   datetime_taken: "2023-08-15T19:30:00Z"
 * };
 *
 * return <PhotoCard photo={photoData} />;
 */
const PhotoCard = ({ photo }) => {
  const photoUrl = `/gallery/photo/${photo.slug}/`;

  /**
   * Преобразует строку даты в отформатированную дату на русском языке.
   *
   * @function
   * @param {string|null} dateString - Строка даты в ISO формате
   * @return {string|null} Отформатированная дата в формате DD.MM.YYYY или null если дата некорректна
   */
  const formatDate = (dateString) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return null;
      return date.toLocaleDateString('ru-RU');
    } catch (error) {
      return null;
    }
  };

  const formattedDate = formatDate(photo.datetime_taken);

  return (
    <Card className="shadow bg-white rounded h-100">
      {photo.thumbnail_url && (
        <a href={photoUrl}>
          <Card.Img
            variant="top"
            src={photo.thumbnail_url}
            alt={photo.name}
            loading="lazy"
          />
        </a>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title>
          <a href={photoUrl} className="text-decoration-none text-dark">
            {photo.name}
          </a>
        </Card.Title>
        {formattedDate && (
          <Card.Text className="text-muted small mt-auto">
            {formattedDate}
          </Card.Text>
        )}
      </Card.Body>
    </Card>
  );
};

PhotoCard.propTypes = {
  photo: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    thumbnail_url: PropTypes.string,
    datetime_taken: PropTypes.string,
  }).isRequired,
};

export default PhotoCard;
