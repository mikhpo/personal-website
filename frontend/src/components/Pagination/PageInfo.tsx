import React from 'react';

/** Свойства компонента информации о текущей странице. */
export interface PageInfoProps {
  currentPage: number;
  totalPages: number;
}

/**
 * Компонент для отображения информации о текущей странице.
 *
 * @return Элемент с информацией о странице или null, если страниц меньше двух
 */
const PageInfo = ({ currentPage, totalPages }: PageInfoProps) => {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <span className="current mx-2">
      страница {currentPage} из {totalPages}
    </span>
  );
};

export default PageInfo;
