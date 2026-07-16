import React from 'react';
import { Button } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент навигации между фотографиями.
 *
 * Отображает кнопки "Предыдущая" и "Следующая" для перемещения между фото в альбоме.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Object|null} props.previousPhoto - Объект предыдущей фотографии
 * @param {string} props.previousPhoto.slug - Слаг предыдущей фотографии
 * @param {Object|null} props.nextPhoto - Объект следующей фотографии
 * @param {string} props.nextPhoto.slug - Слаг следующей фотографии
 * @return {JSX.Element|null} Компонент навигации или null
 */
const PhotoNavigation = ({ previousPhoto, nextPhoto }) => {
  if (!previousPhoto && !nextPhoto) {
    return null;
  }

  return (
    <div className="d-flex justify-content-between mt-3">
      <div>
        {previousPhoto && (
          <Button
            variant="primary"
            href={`/gallery/photo/${previousPhoto.slug}/`}
          >
            ← Предыдущая
          </Button>
        )}
      </div>
      <div>
        {nextPhoto && (
          <Button
            variant="primary"
            href={`/gallery/photo/${nextPhoto.slug}/`}
          >
            Следующая →
          </Button>
        )}
      </div>
    </div>
  );
};

PhotoNavigation.propTypes = {
  previousPhoto: PropTypes.shape({
    slug: PropTypes.string.isRequired,
  }),
  nextPhoto: PropTypes.shape({
    slug: PropTypes.string.isRequired,
  }),
};

export default PhotoNavigation;
