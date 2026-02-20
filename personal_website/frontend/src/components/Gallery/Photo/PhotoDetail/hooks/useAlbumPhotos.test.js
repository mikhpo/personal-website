import { renderHook, act } from '@testing-library/react';
import useAlbumPhotos from '@components/Gallery/Photo/PhotoDetail/hooks/useAlbumPhotos';

/**
 * Тесты для хука useAlbumPhotos.
 *
 * Хук useAlbumPhotos предназначен для загрузки фотографий альбома из API.
 * Тесты проверяют корректность работы хука в различных сценариях:
 * - Инициализация с правильными начальными значениями
 * - Загрузка фотографий альбома при монтировании
 * - Обработка ошибок загрузки (HTTP ошибки и сетевые ошибки)
 * - Повторная загрузка данных после ошибки
 * - Поведение при различных значениях albumId (null, undefined, 0)
 * - Работа с кастомным URL API
 * - Перезагрузка данных при изменении параметров (albumId, apiUrl)
 * - Обработка различных форматов ответа API
 */
describe('useAlbumPhotos', () => {
  const mockPhotos = [
    { id: 1, name: 'Фото 1', slug: 'photo-1' },
    { id: 2, name: 'Фото 2', slug: 'photo-2' },
    { id: 3, name: 'Фото 3', slug: 'photo-3' },
  ];

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /**
   * Проверяет, что хук инициализируется с правильными начальными значениями:
   * - photos: пустой массив
   * - loading: true (в процессе загрузки)
   * - error: null (нет ошибки)
   */
  test('инициализируется с правильными начальными значениями', () => {
    // Мокаем fetch чтобы не делать реальный запрос
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
  });

  /**
   * Проверяет, что хук правильно загружает фотографии альбома при монтировании:
   * - Отправляет запрос к API с правильным URL
   * - После получения данных устанавливает photos в массив фотографий
   * - Устанавливает loading в false
   * - Устанавливает error в null
   */
  test('загружает фотографии альбома при монтировании', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    expect(result.current.loading).toBe(true);

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual(mockPhotos);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Проверяет обработку HTTP ошибок при загрузке фотографий:
   * - При получении ответа с ok: false устанавливает соответствующее сообщение об ошибке
   * - Устанавливает photos в пустой массив
   * - Устанавливает loading в false
   * - Устанавливает error в строку с кодом ошибки
   */
  test('обрабатывает ошибку загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    expect(result.current.loading).toBe(true);

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Ошибка загрузки фотографий альбома: 404');
  });

  /**
   * Проверяет обработку сетевых ошибок при загрузке фотографий:
   * - При возникновении ошибки сети устанавливает сообщение об ошибке
   * - Устанавливает photos в пустой массив
   * - Устанавливает loading в false
   * - Устанавливает error в сообщение об ошибке
   */
  test('обрабатывает network error', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useAlbumPhotos(1));

    expect(result.current.loading).toBe(true);

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Network error');
  });

  /**
   * Проверяет возможность повторной загрузки данных после ошибки:
   * - При вызове функции refetch() происходит новая попытка загрузки данных
   * - После успешной повторной загрузки данные обновляются
   * - Состояния loading и error обновляются соответственно
   */
  test('повторная загрузка работает после ошибки', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockPhotos }),
      });

    const { result } = renderHook(() => useAlbumPhotos(1));

    // Дождаться первой загрузки с ошибкой
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Ошибка загрузки фотографий альбома: 500');

    // Выполнить повторную загрузку
    await act(async () => {
      result.current.refetch();
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual(mockPhotos);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Проверяет, что хук не выполняет загрузку данных, если albumId равен null:
   * - Функция fetch не вызывается
   * - photos остается пустым массивом
   * - loading устанавливается в false
   * - error остается null
   */
  test('не загружает данные если albumId null', async () => {
    const { result } = renderHook(() => useAlbumPhotos(null));

    // Функция fetch не должна быть вызвана
    expect(global.fetch).not.toHaveBeenCalled();

    // Состояние должно быть "загружено" без данных
    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Проверяет, что хук не выполняет загрузку данных, если albumId равен undefined:
   * - Функция fetch не вызывается
   * - photos остается пустым массивом
   * - loading устанавливается в false
   * - error остается null
   */
  test('не загружает данные если albumId undefined', async () => {
    const { result } = renderHook(() => useAlbumPhotos(undefined));

    // Функция fetch не должна быть вызвана
    expect(global.fetch).not.toHaveBeenCalled();

    // Состояние должно быть "загружено" без данных
    expect(result.current.photos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Проверяет, что хук использует кастомный URL API при его указании:
   * - Функция fetch вызывается с правильным кастомным URL
   * - Данные загружаются и обрабатываются аналогично основному сценарию
   * - photos заполняется массивом фотографий
   * - loading устанавливается в false после загрузки
   * - error остается null при успешной загрузке
   */
  test('использует кастомный apiUrl', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });

    const { result } = renderHook(() => useAlbumPhotos(1, '/custom/api/'));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/custom/api/?album=1');
    expect(result.current.photos).toEqual(mockPhotos);
  });

  /**
   * Проверяет перезагрузку данных при изменении параметра albumId:
   * - При изменении albumId происходит новая загрузка с обновленным параметром
   * - Функция fetch вызывается с новым значением albumId в URL
   * - Данные обновляются в соответствии с новым albumId
   */
  test('перезагружает данные при изменении albumId', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });

    const { rerender } = renderHook(
      ({ albumId }) => useAlbumPhotos(albumId),
      { initialProps: { albumId: 1 } }
    );

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/?album=1');

    // Изменить albumId
    rerender({ albumId: 2 });

    // Дождаться новой загрузки
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/?album=2');
  });

  /**
   * Проверяет перезагрузку данных при изменении параметра apiUrl:
   * - При изменении apiUrl происходит новая загрузка с обновленным URL
   * - Функция fetch вызывается с новым значением apiUrl
   * - Данные обновляются в соответствии с новым URL API
   */
  test('перезагружает данные при изменении apiUrl', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });

    const { rerender } = renderHook(
      ({ apiUrl }) => useAlbumPhotos(1, apiUrl),
      { initialProps: { apiUrl: '/api/gallery/photos/' } }
    );

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/?album=1');

    // Изменить apiUrl
    rerender({ apiUrl: '/custom/api/' });

    // Дождаться новой загрузки
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(global.fetch).toHaveBeenCalledWith('/custom/api/?album=1');
  });

  /**
   * Проверяет обработку ответа API, который сразу возвращает массив без обертки results:
   * - При получении прямого массива photos устанавливается в этот массив
   * - Корректно обрабатывает различные форматы ответа от API
   */
  test('обрабатывает прямой массив без results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPhotos,
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual(mockPhotos);
  });

  /**
   * Проверяет обработку пустого объекта в ответе API:
   * - При получении пустого объекта photos устанавливается в пустой массив
   * - Корректно обрабатывает граничные случаи формата ответа
   */
  test('обрабатывает пустой объект ответа', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual([]);
  });

  /**
   * Проверяет обработку случая, когда в results содержится не массив:
   * - При получении не-массива в поле results photos устанавливается в пустой массив
   * - Защита от некорректных данных в ответе API
   */
  test('обрабатывает не-массив в results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: 'not an array' }),
    });

    const { result } = renderHook(() => useAlbumPhotos(1));

    // Дождаться завершения асинхронной операции
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.photos).toEqual([]);
  });
});