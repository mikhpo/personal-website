import React from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент карточки серии блога.
 *
 * Отображает превью серии с изображением, названием и описанием.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.series - Объект серии
 * @param {number} props.series.id - ID серии (первичный ключ)
 * @param {string} props.series.name - Название серии
 * @param {string} props.series.slug - Слаг серии для URL
 * @param {string} [props.series.description] - Описание серии
 * @param {string} [props.series.image] - URL изображения серии
 * @return {JSX.Element} Компонент карточки серии
 *
 * @example
 * <SeriesCard series={{
 *   id: 1,
 *   name: "Лангтанг-трек",
 *   slug: "langtang-trek",
 *   description: "Поход в Непале",
 *   image: "/media/blog/series/langtang.jpg"
 * }} />
 */
const SeriesCard = ({ series }) => {
  const seriesUrl = `/blog/series/${series.slug}/`;

  return (
    <Card className="shadow bg-white rounded text-center h-100">
      {series.image && (
        <a href={seriesUrl}>
          <Card.Img
            variant="top"
            src={series.image}
            alt={series.name}
            loading="lazy"
          />
        </a>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title className="mt-auto" as="h6">
          <a href={seriesUrl} className="text-decoration-none text-dark">
            {series.name}
          </a>
        </Card.Title>
        {series.description && (
          <Card.Text>
            <a href={seriesUrl} className="text-decoration-none text-dark">
              {series.description}
            </a>
          </Card.Text>
        )}
      </Card.Body>
    </Card>
  );
};

SeriesCard.propTypes = {
  series: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    description: PropTypes.string,
    image: PropTypes.string,
  }).isRequired,
};

export default SeriesCard;
