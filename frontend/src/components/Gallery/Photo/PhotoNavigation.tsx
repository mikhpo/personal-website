import React from 'react';
import { Button } from 'react-bootstrap';
import type { components } from '../../../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Свойства компонента навигации между фотографиями. */
export interface PhotoNavigationProps {
  /** Предыдущая фотография или null. */
  previousPhoto?: Photo | null;
  /** Следующая фотография или null. */
  nextPhoto?: Photo | null;
}

/**
 * Компонент навигации между фотографиями.
 *
 * Отображает кнопки "Предыдущая" и "Следующая" для перемещения между
 * фото в альбоме.
 */
const PhotoNavigation = ({ previousPhoto, nextPhoto }: PhotoNavigationProps) => {
  if (!previousPhoto && !nextPhoto) {
    return null;
  }

  return (
    <div className="d-flex justify-content-between mt-3">
      <div>
        {previousPhoto && (
          <Button variant="primary" href={`/gallery/photo/${previousPhoto.slug}/`}>
            ← Предыдущая
          </Button>
        )}
      </div>
      <div>
        {nextPhoto && (
          <Button variant="primary" href={`/gallery/photo/${nextPhoto.slug}/`}>
            {'Следующая ->'}
          </Button>
        )}
      </div>
    </div>
  );
};

export default PhotoNavigation;
