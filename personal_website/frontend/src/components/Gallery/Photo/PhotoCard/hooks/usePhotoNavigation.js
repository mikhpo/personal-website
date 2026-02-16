/**
 * Хук для вычисления навигации между фотографиями в альбоме.
 *
 * Вычисляет предыдущую и следующую фотографии на основе текущей фотографии
 * и списка фотографий альбома, отсортированных по дате съемки.
 *
 * @param {Object|null} photo - Текущая фотография
 * @param {Array} albumPhotos - Массив фотографий альбома
 * @return {Object} Объект с предыдущей и следующей фотографиями
 * @property {Object|null} previousPhoto - Предыдущая фотография или null
 * @property {Object|null} nextPhoto - Следующая фотография или null
 */
const usePhotoNavigation = (photo, albumPhotos) => {
  // Если нет фотографии или списка фотографий, возвращаем null для обеих
  if (!photo || !albumPhotos || albumPhotos.length === 0) {
    return {
      previousPhoto: null,
      nextPhoto: null
    };
  }

  // Проверяем, есть ли фотографии с datetime_taken
  const photosWithDates = albumPhotos.filter(p => p.datetime_taken);
  const hasDates = photosWithDates.length > 0;
  const hasNullDates = albumPhotos.some(p => !p.datetime_taken);
  
  // Если есть смешанные даты (некоторые с датами, некоторые без), возвращаем null для обеих
  // Это упрощенный подход для обработки смешанных данных
  if (hasDates && hasNullDates) {
    return {
      previousPhoto: null,
      nextPhoto: null
    };
  }
  
  // Если нет ни одной даты, возвращаем null для обеих
  if (!hasDates) {
    return {
      previousPhoto: null,
      nextPhoto: null
    };
  }

  // Сортируем фотографии по дате съемки (все имеют даты)
  const sortedPhotos = [...albumPhotos].sort((a, b) => {
    return new Date(a.datetime_taken) - new Date(b.datetime_taken);
  });

  // Находим индекс текущей фотографии
  const currentIndex = sortedPhotos.findIndex(p => p.id === photo.id);

  // Если фотография не найдена в списке, возвращаем null для обеих
  if (currentIndex === -1) {
    return {
      previousPhoto: null,
      nextPhoto: null
    };
  }

  // Вычисляем предыдущую и следующую фотографии
  const previousPhoto = currentIndex > 0 ? sortedPhotos[currentIndex - 1] : null;
  const nextPhoto = currentIndex < sortedPhotos.length - 1 ? sortedPhotos[currentIndex + 1] : null;

  return {
    previousPhoto,
    nextPhoto
  };
};

export default usePhotoNavigation;