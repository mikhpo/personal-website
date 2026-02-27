/**
 * Хук для вычисления навигации между фотографиями в альбоме.
 *
 * Вычисляет предыдущую и следующую фотографии на основе текущей фотографии
 * и списка фотографий альбома, отсортированных по дате съемки.
 * Если дата съемки недоступна, используется дата загрузки как запасной вариант.
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

  /**
   * Получить значение для сортировки: предпочитаем datetime_taken, иначе uploaded_at.
   *
   * @param {Object} p - Объект фотографии
   * @return {number} Метка времени в миллисекундах
   */
  const getSortKey = (p) => {
    const dateStr = p.datetime_taken || p.uploaded_at;
    return dateStr ? new Date(dateStr).getTime() : 0;
  };

  // Сортируем фотографии по дате съемки (от ранних к поздним)
  const sortedPhotos = [...albumPhotos].sort((a, b) => getSortKey(a) - getSortKey(b));

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
