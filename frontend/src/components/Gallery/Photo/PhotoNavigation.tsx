import React from 'react';

/** Свойства компонента навигации между фотографиями. */
export interface PhotoNavigationProps {
  /** URL предыдущей фотографии или null. */
  previousUrl: string | null;
  /** URL следующей фотографии или null. */
  nextUrl: string | null;
  /** Действия между стрелками навигации (кнопки "О фото" и других модальных окон). */
  children?: React.ReactNode;
}

/**
 * Компонент навигации между фотографиями.
 *
 * Рендерит стрелки перехода к предыдущей и следующей фотографии альбома;
 * между ними размещаются дочерние действия страницы (кнопки модальных окон).
 */
const PhotoNavigation = ({ previousUrl, nextUrl, children }: PhotoNavigationProps) => {
  return (
    <>
      {previousUrl && (
        <a
          href={previousUrl}
          className="btn btn-outline-dark"
          id="previous-photo-link"
          aria-label="Предыдущая фотография"
        >
          {'<'}
        </a>
      )}
      {children}
      {nextUrl && (
        <a href={nextUrl} className="btn btn-outline-dark" id="next-photo-link" aria-label="Следующая фотография">
          {'>'}
        </a>
      )}
    </>
  );
};

export default PhotoNavigation;
