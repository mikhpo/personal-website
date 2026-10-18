import React from 'react';
import { Button } from 'react-bootstrap';
import type { components } from '../../../types/api-schema';

type Tag = components['schemas']['Tag'];

/** Свойства компонента кнопки тега. */
export interface TagButtonProps {
  /** Объект тега. */
  tag: Tag;
  /** Обработчик клика на кнопку. */
  onClick?: (tag: Tag) => void;
}

/**
 * Компонент кнопки для одного тега.
 *
 * Отображает кнопку-ссылку на страницу тега с опциональным обработчиком клика.
 */
const TagButton = ({ tag, onClick }: TagButtonProps) => {
  const tagUrl = `/gallery/tag/${tag.slug}/`;

  const handleClick = () => {
    if (onClick) {
      onClick(tag);
    }
  };

  return (
    <Button variant="outline-dark" href={tagUrl} onClick={handleClick} className="w-100">
      {tag.name}
    </Button>
  );
};

export default TagButton;
