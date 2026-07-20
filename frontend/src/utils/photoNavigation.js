/**
 * Утилита для вычисления навигации между фотографиями в альбоме.
 *
 * Вычисляет предыдущую и следующую фотографии на основе текущей фотографии
 * и списка фотографий альбома в порядке API.
 *
 * @param {Object|null} photo - Текущая фотография
 * @param {Array} albumPhotos - Массив фотографий альбома (в порядке API)
 * @return {Object} Объект с предыдущей и следующей фотографиями
 * @property {Object|null} previousPhoto - Предыдущая фотография или null
 * @property {Object|null} nextPhoto - Следующая фотография или null
 */
const getPhotoNavigation = (photo, albumPhotos) => {
  // Если нет фотографии или списка фотографий, возвращаем null для обеих
  if (!photo || !albumPhotos || !Array.isArray(albumPhotos) || albumPhotos.length === 0) {
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
  let previousPhoto = null;
  if (currentIndex > 0) {
    previousPhoto = albumPhotos[currentIndex - 1];
  }

  // Вычисляем следующую фотографию
  let nextPhoto = null;
  if (currentIndex < albumPhotos.length - 1) {
    nextPhoto = albumPhotos[currentIndex + 1];
  }

  return {
    previousPhoto,
    nextPhoto,
  };
};

export default getPhotoNavigation;
