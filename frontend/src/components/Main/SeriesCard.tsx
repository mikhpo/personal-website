import React from 'react';
import BaseCard from '@components/Card/BaseCard';
import type { components } from '@api-types/api-schema';

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
const SeriesCard = ({ series }: SeriesCardProps) => (
  <BaseCard
    title={series.name}
    url={`/blog/series/${series.slug}/`}
    image={series.image}
    description={series.description}
    imageAlt={series.name}
    titleClassName="fs-6"
  />
);

export default SeriesCard;
