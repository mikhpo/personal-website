import React from 'react';
import { Button } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент кнопки для одного тега.
 *
 * Отображает кнопку-ссылку на страницу тега с опциональным обработчиком клика.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.tag - Объект тега
 * @param {number} props.tag.id - ID тега
 * @param {string} props.tag.name - Название тега
 * @param {string} props.tag.slug - Слаг тега для URL
 * @param {Function} [props.onClick] - Обработчик клика на кнопку
 * @return {JSX.Element} Компонент кнопки тега
 */
const TagButton = ({ tag, onClick }) => {
  const tagUrl = `/gallery/tag/${tag.slug}/`;

  const handleClick = (e) => {
    if (onClick) {
      onClick(tag);
    }
  };

  return (
    <Button
      variant="outline-dark"
      href={tagUrl}
      onClick={handleClick}
      className="w-100"
    >
      {tag.name}
    </Button>
  );
};

TagButton.propTypes = {
  tag: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
  }).isRequired,
  onClick: PropTypes.func,
};

export default TagButton;
