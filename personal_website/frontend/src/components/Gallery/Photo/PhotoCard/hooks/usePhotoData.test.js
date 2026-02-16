import { renderHook, act } from '@testing-library/react';
import usePhotoData from '@components/Gallery/Photo/PhotoCard/hooks/usePhotoData';

/**
 * Тесты для хука usePhotoData
 * 
 * Хук usePhotoData предназначен для загрузки данных фотографии по slug из API.
 * Тесты проверяют корректность работы хука в различных сценариях:
 * - Инициализация с правильными начальными значениями
 * - Загрузка данных фотографии
 * - Обработка ошибок загрузки
 * - Повторная загрузка после ошибки
 * - Работа с пустыми значениями slug
 * - Использование кастомного URL API
 * - Реакция на изменение параметров
 */
describe('usePhotoData', () => {
  const mockPhoto = {
    id: 1,
    name: 'Тестовое фото',
    slug: 'test-photo',
    description: 'Описание фото',
    image_url: '/media/photo.jpg',
  };

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /**
   * Тест проверяет, что хук инициализируется с правильными начальными значениями:
   * - photo: null
   * - loading: true
   * - error: null
   */
  test('инициализируется с правильными начальными значениями', () => {
    // Мокаем fetch чтобы не делать реальный запрос
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPhoto,
    });

    const { result } = renderHook(() => usePhotoData('test-photo'));

    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
  });

  /**
   * Тест проверяет, что хук корректно загружает данные фотографии при монтировании:
   * - Выполняется fetch-запрос к API
   * - После получения данных photo содержит объект с данными
   * - loading устанавливается в false
   * - error остается null
   */
  test('загружает данные фотографии при монтировании', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPhoto,
    });

    const { result } = renderHook(() => usePhotoData('test-photo'));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photo).toEqual(mockPhoto);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Тест проверяет обработку ошибок загрузки:
   * - При получении ответа с ok: false устанавливается сообщение об ошибке
   * - loading устанавливается в false
   * - photo остается null
   */
  test('обрабатывает ошибку загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const { result } = renderHook(() => usePhotoData('test-photo'));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Ошибка загрузки фото: 404');
  });

  /**
   * Тест проверяет обработку сетевых ошибок:
   * - При отклонении fetch-запроса устанавливается сообщение об ошибке
   * - loading устанавливается в false
   * - photo остается null
   */
  test('обрабатывает network error', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => usePhotoData('test-photo'));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Network error');
  });

  /**
   * Тест проверяет функцию повторной загрузки (refetch):
   * - После ошибки можно вызвать refetch для повторной попытки
   * - При успешной повторной загрузке данные устанавливаются корректно
   * - error очищается
   */
  test('повторная загрузка работает после ошибки', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockPhoto,
      });

    const { result } = renderHook(() => usePhotoData('test-photo'));

    // Дождаться первой загрузки с ошибкой
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Ошибка загрузки фото: 500');

    // Выполнить повторную загрузку
    await act(async () => {
      result.current.refetch();
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photo).toEqual(mockPhoto);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Тест проверяет, что хук не выполняет загрузку при пустом значении photoSlug:
   * - fetch не вызывается
   * - Состояние устанавливается как "загружено" без данных
   */
  test('не загружает данные если photoSlug пустой', async () => {
    const { result } = renderHook(() => usePhotoData(''));

    // Функция fetch не должна быть вызвана сразу
    expect(global.fetch).not.toHaveBeenCalled();

    // Состояние должно быть "загружено" без данных
    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
  });

  /**
   * Тест проверяет, что хук не выполняет загрузку при null в photoSlug:
   * - fetch не вызывается
   * - Состояние устанавливается как "загружено" без данных
   */
  test('не загружает данные если photoSlug null', async () => {
    const { result } = renderHook(() => usePhotoData(null));

    // Функция fetch не должна быть вызвана сразу
    expect(global.fetch).not.toHaveBeenCalled();

    // Состояние должно быть "загружено" без данных
    expect(result.current.photo).toBeNull();
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
  });

  /**
   * Тест проверяет использование кастомного apiUrl:
   * - Запрос выполняется к указанному URL
   * - Данные загружаются корректно
   */
  test('использует кастомный apiUrl', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPhoto,
    });

    const { result } = renderHook(() => usePhotoData('test-photo', '/custom/api/'));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/custom/api/test-photo/');
    expect(result.current.photo).toEqual(mockPhoto);
  });

  /**
   * Тест проверяет, что хук перезагружает данные при изменении photoSlug:
   * - При изменении параметра photoSlug выполняется новый запрос
   * - Запрос отправляется к правильному URL
   */
  test('перезагружает данные при изменении photoSlug', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockPhoto,
    });

    const { rerender } = renderHook(
      ({ photoSlug }) => usePhotoData(photoSlug),
      { initialProps: { photoSlug: 'photo-1' } }
    );

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/photo-1/');

    // Изменить photoSlug
    rerender({ photoSlug: 'photo-2' });

    // Дождаться новой загрузки
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/photo-2/');
  });

  /**
   * Тест проверяет, что хук перезагружает данные при изменении apiUrl:
   * - При изменении параметра apiUrl выполняется новый запрос
   * - Запрос отправляется к правильному URL
   */
  test('перезагружает данные при изменении apiUrl', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockPhoto,
    });

    const { rerender } = renderHook(
      ({ apiUrl }) => usePhotoData('test-photo', apiUrl),
      { initialProps: { apiUrl: '/api/gallery/photos/' } }
    );

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/test-photo/');

    // Изменить apiUrl
    rerender({ apiUrl: '/custom/api/' });

    // Дождаться новой загрузки
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/custom/api/test-photo/');
  });
});