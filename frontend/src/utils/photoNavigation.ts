/**
 * Утилита для вычисления навигации между фотографиями в альбоме.
 *
 * Вычисляет предыдущую и следующую фотографии на основе текущей фотографии
 * и списка фотографий альбома в порядке API.
 */

import type { components } from '../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Результат вычисления навигации по фотографиям альбома. */
export interface PhotoNavigationResult {
  previousPhoto: Photo | null;
  nextPhoto: Photo | null;
}

/**
 * Вычисляет предыдущую и следующую фотографии для текущей.
 */
const getPhotoNavigation = (photo: Photo | null, albumPhotos: Photo[] | null | undefined): PhotoNavigationResult => {
  // Если нет фотографии или списка фотографий, возвращаем null для обеих
  if (!photo || !albumPhotos || albumPhotos.length === 0) {
    return {
      previousPhoto: null,
      nextPhoto: null,
    };
  }

  // Находим индекс текущей фотографии по ID
  const currentIndex = albumPhotos.findIndex((p) => p.id === photo.id);

  // Если фотография не найдена в списке, возвращаем null для обеих
  if (currentIndex === -1) {
    return {
      previousPhoto: null,
      nextPhoto: null,
    };
  }

  // Вычисляем предыдущую фотографию
  let previousPhoto: Photo | null = null;
  if (currentIndex > 0) {
    previousPhoto = albumPhotos[currentIndex - 1] ?? null;
  }

  // Вычисляем следующую фотографию
  let nextPhoto: Photo | null = null;
  if (currentIndex < albumPhotos.length - 1) {
    nextPhoto = albumPhotos[currentIndex + 1] ?? null;
  }

  return {
    previousPhoto,
    nextPhoto,
  };
};

export default getPhotoNavigation;
