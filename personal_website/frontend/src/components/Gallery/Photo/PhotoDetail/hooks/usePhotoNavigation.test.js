import usePhotoNavigation from '@components/Gallery/Photo/PhotoDetail/hooks/usePhotoNavigation';

/**
 * Тесты для хука usePhotoNavigation.
 * 
 * Хук usePhotoNavigation используется для вычисления навигации между фотографиями в альбоме.
 * Он определяет предыдущую и следующую фотографии на основе текущей фотографии и списка
 * всех фотографий в альбоме, отсортированных по дате съемки.
 */
describe('usePhotoNavigation', () => {
  const mockPhotos = [
    { id: 1, slug: 'photo-1', datetime_taken: '2024-01-14T10:00:00Z' },
    { id: 2, slug: 'photo-2', datetime_taken: '2024-01-15T10:00:00Z' },
    { id: 3, slug: 'photo-3', datetime_taken: '2024-01-16T10:00:00Z' },
  ];

  const currentPhoto = mockPhotos[1]; // photo-2

  /**
   * Тест проверяет, что хук правильно возвращает предыдущую и следующую фотографии
   * для фотографии в середине списка.
   */
  test('возвращает правильные previous и next фото', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, mockPhotos);
    expect(previousPhoto).toEqual(mockPhotos[0]); // photo-1
    expect(nextPhoto).toEqual(mockPhotos[2]); // photo-3
  });

  /**
   * Тест проверяет, что хук возвращает null для предыдущей фотографии,
   * если текущая фотография является первой в альбоме.
   */
  test('возвращает null для previous если фото первое', () => {
    const firstPhoto = mockPhotos[0]; // photo-1
    const { previousPhoto, nextPhoto } = usePhotoNavigation(firstPhoto, mockPhotos);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toEqual(mockPhotos[1]); // photo-2
  });

  /**
   * Тест проверяет, что хук возвращает null для следующей фотографии,
   * если текущая фотография является последней в альбоме.
   */
  test('возвращает null для next если фото последнее', () => {
    const lastPhoto = mockPhotos[2]; // photo-3
    const { previousPhoto, nextPhoto } = usePhotoNavigation(lastPhoto, mockPhotos);
    expect(previousPhoto).toEqual(mockPhotos[1]); // photo-2
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если в альбоме только одна фотография.
   */
  test('возвращает null для обоих если фото единственное в альбоме', () => {
    const singlePhoto = mockPhotos[1]; // photo-2
    const { previousPhoto, nextPhoto } = usePhotoNavigation(singlePhoto, [singlePhoto]);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если передана null вместо текущей фотографии.
   */
  test('возвращает null для обоих если photo null', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(null, mockPhotos);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если передан пустой массив фотографий.
   */
  test('возвращает null для обоих если albumPhotos пустой массив', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, []);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если передан null вместо массива фотографий.
   */
  test('возвращает null для обоих если albumPhotos null', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, null);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если массив фотографий не определен (undefined).
   */
  test('возвращает null для обоих если albumPhotos undefined', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, undefined);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если текущая фотография не найдена в списке фотографий альбома.
   */
  test('возвращает null для обоих если фото не найдено в списке', () => {
    const unknownPhoto = { id: 999, slug: 'unknown-photo' };
    const { previousPhoto, nextPhoto } = usePhotoNavigation(unknownPhoto, mockPhotos);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук правильно сортирует фотографии по дате съемки
   * перед определением навигации, даже если они переданы в неотсортированном виде.
   */
  test('сортирует фото по datetime_taken', () => {
    // Неотсортированный список фото
    const unsortedPhotos = [
      { id: 3, slug: 'photo-3', datetime_taken: '2024-01-16T10:00:00Z' },
      { id: 1, slug: 'photo-1', datetime_taken: '2024-01-14T10:00:00Z' },
      { id: 2, slug: 'photo-2', datetime_taken: '2024-01-15T10:00:00Z' },
    ];

    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, unsortedPhotos);

    // Должно вернуть правильные фото несмотря на неотсортированный список
    expect(previousPhoto).toEqual(unsortedPhotos[1]); // photo-1
    expect(nextPhoto).toEqual(unsortedPhotos[0]); // photo-3
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если у всех фотографий отсутствует дата съемки.
   */
  test('обрабатывает фото без datetime_taken', () => {
    const photosWithoutDates = [
      { id: 1, slug: 'photo-1', datetime_taken: null },
      { id: 2, slug: 'photo-2', datetime_taken: null },
      { id: 3, slug: 'photo-3', datetime_taken: null },
    ];

    const { previousPhoto, nextPhoto } = usePhotoNavigation(photosWithoutDates[1], photosWithoutDates);

    // При отсутствии дат все фото сортируются как одинаковые, поэтому navigation не работает корректно
    // Но хук должен корректно обработать такой случай
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук возвращает null для обеих фотографий,
   * если у части фотографий отсутствует дата съемки (смешанные данные).
   */
  test('обрабатывает фото с частично отсутствующими datetime_taken', () => {
    const photosWithPartialDates = [
      { id: 1, slug: 'photo-1', datetime_taken: null },
      { id: 2, slug: 'photo-2', datetime_taken: '2024-01-15T10:00:00Z' },
      { id: 3, slug: 'photo-3', datetime_taken: null },
    ];

    const { previousPhoto, nextPhoto } = usePhotoNavigation(photosWithPartialDates[1], photosWithPartialDates);

    // При смешанных датах навигация может работать непредсказуемо, поэтому возвращаем null для обеих
    // Это упрощенный подход для обработки смешанных данных
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук правильно работает с одним фото в альбоме,
   * возвращая null для обеих фотографий.
   */
  test('работает с одним фото в альбоме', () => {
    const { previousPhoto, nextPhoto } = usePhotoNavigation(currentPhoto, [currentPhoto]);
    expect(previousPhoto).toBeNull();
    expect(nextPhoto).toBeNull();
  });

  /**
   * Тест проверяет, что хук правильно работает с большим количеством фотографий,
   * определяя правильные предыдущую и следующую фотографии.
   */
  test('работает с большим количеством фото', () => {
    const manyPhotos = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      slug: `photo-${i + 1}`,
      datetime_taken: `2024-01-${String(i + 1).padStart(2, '0')}T10:00:00Z`,
    }));

    const middlePhoto = manyPhotos[5]; // photo-6
    const { previousPhoto, nextPhoto } = usePhotoNavigation(middlePhoto, manyPhotos);

    expect(previousPhoto).toEqual(manyPhotos[4]); // photo-5
    expect(nextPhoto).toEqual(manyPhotos[6]); // photo-7
  });
});