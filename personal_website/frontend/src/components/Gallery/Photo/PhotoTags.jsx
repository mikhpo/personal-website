import React from 'react';
import { Badge } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент отображения тегов фотографии.
 *
 * Показывает список тегов в виде badges со ссылками на страницы тегов.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Array<Object>} props.tags - Массив объектов тегов
 * @param {number} props.tags[].id - ID тега
 * @param {string} props.tags[].name - Название тега
 * @param {string} props.tags[].slug - Слаг тега для URL
 * @return {JSX.Element|null} Компонент списка тегов или null
 */
const PhotoTags = ({ tags }) => {
  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <div className="mb-3">
      <h6 className="fw-bold mb-2">Тэги:</h6>
      <div className="d-flex flex-wrap gap-2">
        {tags.map(tag => (
          <a
            key={tag.id}
            href={`/gallery/tag/${tag.slug}/`}
            className="text-decoration-none"
          >
            <Badge bg="secondary">{tag.name}</Badge>
          </a>
        ))}
      </div>
    </div>
  );
};

PhotoTags.propTypes = {
  tags: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      slug: PropTypes.string.isRequired,
    })
  ),
};

export default PhotoTags;
