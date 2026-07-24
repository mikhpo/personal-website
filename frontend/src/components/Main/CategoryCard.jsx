import React from 'react';
import PropTypes from 'prop-types';
import BaseCard from '@components/Card/BaseCard';

/**
 * Компонент карточки категории блога.
 *
 * Отображает превью категории с изображением, названием и описанием.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.category - Объект категории
 * @param {number} props.category.id - ID категории (первичный ключ)
 * @param {string} props.category.name - Название категории
 * @param {string} props.category.slug - Слаг категории для URL
 * @param {string} [props.category.description] - Описание категории
 * @param {string} [props.category.image] - URL изображения категории
 * @return {JSX.Element} Компонент карточки категории
 *
 * @example
 * <CategoryCard category={{
 *   id: 1,
 *   name: "Разработка",
 *   slug: "razrabotka",
 *   description: "Статьи о разработке",
 *   image: "/media/blog/categories/dev.jpg"
 * }} />
 */
const CategoryCard = ({ category }) => {
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

CategoryCard.propTypes = {
  category: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    description: PropTypes.string,
    image: PropTypes.string,
  }).isRequired,
};

export default CategoryCard;
