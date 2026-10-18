import React from 'react';
import { Card } from 'react-bootstrap';
import type { components } from '../../types/api-schema';

type Series = components['schemas']['Series'];

/** Свойства компонента карточки серии. */
export interface SeriesCardProps {
  series: Series;
}

/**
 * Компонент карточки серии блога.
 *
 * Отображает превью серии с изображением, названием и описанием.
 *
 * @example
 * <SeriesCard
 *   series={{
 *     id: 1,
 *     name: 'Лангтанг-трек',
 *     slug: 'langtang-trek',
 *     description: 'Поход в Непале',
 *     image: '/media/blog/series/langtang.jpg',
 *   }}
 * />
 */
const SeriesCard = ({ series }: SeriesCardProps) => {
  const seriesUrl = `/blog/series/${series.slug}/`;

  return (
    <Card className="shadow rounded text-center h-100">
      {series.image && (
        <a href={seriesUrl}>
          <Card.Img variant="top" src={series.image} alt={series.name} loading="lazy" />
        </a>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title className="mt-auto fs-6" as="h3">
          <a href={seriesUrl} className="text-decoration-none text-body">
            {series.name}
          </a>
        </Card.Title>
        {series.description && (
          <Card.Text>
            {/* Описание кликабельно, как и название, но без подчеркивания - карточка не должна выглядеть как набор ссылок */}
            <a href={seriesUrl} className="text-decoration-none text-body">
              {series.description}
            </a>
          </Card.Text>
        )}
      </Card.Body>
    </Card>
  );
};

export default SeriesCard;
