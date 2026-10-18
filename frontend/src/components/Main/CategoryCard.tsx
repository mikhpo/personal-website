import React from 'react';
import BaseCard from '@components/Card/BaseCard';
import type { components } from '../../types/api-schema';

type Category = components['schemas']['Category'];

/** Свойства компонента карточки категории. */
export interface CategoryCardProps {
  category: Category;
}

/**
 * Компонент карточки категории блога.
 *
 * Отображает превью категории с изображением, названием и описанием.
 *
 * @example
 * <CategoryCard
 *   category={{
 *     id: 1,
 *     name: 'Разработка',
 *     slug: 'razrabotka',
 *     description: 'Статьи о разработке',
 *     image: '/media/blog/categories/dev.jpg',
 *   }}
 * />
 */
const CategoryCard = ({ category }: CategoryCardProps) => {
  const categoryUrl = `/blog/category/${category.slug}/`;

  return (
    <BaseCard
      title={category.name}
      url={categoryUrl}
      image={category.image}
      description={category.description}
      imageAlt={category.name}
    />
  );
};

export default CategoryCard;
