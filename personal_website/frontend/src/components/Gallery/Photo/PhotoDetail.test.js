import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoDetail from './PhotoDetail/PhotoDetail';

// Мокаем хуки
jest.mock('./PhotoDetail/hooks/usePhotoData');
jest.mock('./PhotoDetail/hooks/useAlbumPhotos');
jest.mock('./PhotoDetail/hooks/usePhotoNavigation');

import usePhotoData from './PhotoDetail/hooks/usePhotoData';
import useAlbumPhotos from './PhotoDetail/hooks/useAlbumPhotos';
import usePhotoNavigation from './PhotoDetail/hooks/usePhotoNavigation';

/**
 * Тестовый набор для компонента PhotoDetail.
 *
 * Проверяет корректность отображения детальной информации о фотографии,
 * навигацию между фотографиями в альбоме, обработку ошибок загрузки
 * и различные граничные случаи.
 */
describe('PhotoDetail', () => {
  const mockPhoto = {
    id: 2,
    name: 'Тестовое фото',
    slug: 'test-photo',
    description: 'Описание фото',
    image_url: '/media/photo.jpg',
    album: 1,
    tags: [
      { id: 1, name: 'Природа', slug: 'nature' },
      { id: 2, name: 'Пейзаж', slug: 'landscape' },
    ],
    camera: 'Canon EOS 5D',
    datetime_taken: '2024-01-15T10:00:00Z',
  };

  const mockAlbumPhotos = [
    { id: 1, slug: 'photo-1', datetime_taken: '2024-01-14T10:00:00Z' },
    { id: 2, slug: 'photo-2', datetime_taken: '2024-01-15T10:00:00Z' },
    { id: 3, slug: 'photo-3', datetime_taken: '2024-01-16T10:00:00Z' },
  ];

  const mockPreviousPhoto = mockAlbumPhotos[0];
  const mockNextPhoto = mockAlbumPhotos[2];

  beforeEach(() => {
    usePhotoData.mockReturnValue({
      photo: mockPhoto,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    
    useAlbumPhotos.mockReturnValue({
      photos: mockAlbumPhotos,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    
    usePhotoNavigation.mockReturnValue({
      previousPhoto: mockPreviousPhoto,
      nextPhoto: mockNextPhoto,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверяет, что компонент корректно отображает данные фотографии после загрузки.
   * Должен отображать название, описание и изображение фотографии.
   */
  test('рендерит фото после загрузки', async () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    await waitFor(() => {
      expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
      expect(screen.getByText('Описание фото')).toBeInTheDocument();
      expect(screen.getByAltText('Тестовое фото')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение индикатора загрузки при загрузке фотографии.
   * Должен отображать сообщение "Загрузка фотографии..." во время загрузки.
   */
  test('отображает индикатор загрузки', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: true,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Загрузка фотографии...', { selector: 'p' })).toBeInTheDocument();
  });

  /**
   * Проверяет вызов хуков загрузки данных при монтировании компонента.
   * Должен вызывать usePhotoData и useAlbumPhotos с правильными параметрами.
   */
  test('загружает фото и albumPhotos при монтировании', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(usePhotoData).toHaveBeenCalledWith('test-photo', '/api/gallery/photos/');
    expect(useAlbumPhotos).toHaveBeenCalledWith(1, '/api/gallery/photos/');
  });

  /**
   * Проверяет вычисление навигации между фотографиями.
   * Должен вызывать usePhotoNavigation и отображать кнопки навигации.
   */
  test('вычисляет предыдущую и следующую фотографии', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(usePhotoNavigation).toHaveBeenCalledWith(mockPhoto, mockAlbumPhotos);
    expect(screen.getByText('← Предыдущая')).toBeInTheDocument();
    expect(screen.getByText('Следующая →')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно отображает данные фотографии после загрузки.
   * Должен отображать название, описание и изображение фотографии.
   */
  test('рендерит фото после загрузки', async () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    await waitFor(() => {
      expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
      expect(screen.getByText('Описание фото')).toBeInTheDocument();
      expect(screen.getByAltText('Тестовое фото')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отсутствие кнопки "Предыдущая" при отсутствии предыдущей фотографии.
   * Должен отображать только кнопку "Следующая" если previousPhoto null.
   */
  test('нет кнопки "Предыдущая" если previousPhoto null', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: null,
      nextPhoto: mockNextPhoto,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('← Предыдущая')).not.toBeInTheDocument();
    expect(screen.getByText('Следующая →')).toBeInTheDocument();
  });

  /**
   * Проверяет отсутствие кнопки "Следующая" при отсутствии следующей фотографии.
   * Должен отображать только кнопку "Предыдущая" если nextPhoto null.
   */
  test('нет кнопки "Следующая" если nextPhoto null', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: mockPreviousPhoto,
      nextPhoto: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('← Предыдущая')).toBeInTheDocument();
    expect(screen.queryByText('Следующая →')).not.toBeInTheDocument();
  });

  /**
   * Проверяет обработку ошибки загрузки фотографии.
   * Должен отображать сообщение об ошибке при неудачной загрузке фотографии.
   */
  test('обрабатывает ошибку загрузки фото', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: 'Ошибка загрузки фото: 404',
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText(/Ошибка загрузки фото: 404/)).toBeInTheDocument();
  });

  /**
   * Проверяет обработку ошибки загрузки фотографий альбома.
   * Должен вызывать useAlbumPhotos даже при ошибке, но не отображать ошибку напрямую.
   */
  test('обрабатывает ошибку загрузки albumPhotos', () => {
    useAlbumPhotos.mockReturnValueOnce({
      photos: [],
      loading: false,
      error: 'Ошибка загрузки фотографий альбома: 500',
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);

    // Ошибка albumPhotos не отображается напрямую, но хук должен быть вызван
    expect(useAlbumPhotos).toHaveBeenCalledWith(1, '/api/gallery/photos/');
  });

  /**
   * Проверяет обработку сетевой ошибки при загрузке фотографии.
   * Должен отображать сообщение об ошибке "Network error".
   */
  test('обрабатывает network error', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: 'Network error',
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });

  /**
   * Проверяет функцию повторной загрузки данных после ошибки.
   * Должен вызывать функцию refetch при нажатии кнопки "Повторить".
   */
  test('повторная загрузка работает после ошибки', async () => {
    const user = userEvent.setup();
    const refetchMock = jest.fn();

    // Сначала возвращаем ошибку
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: 'Ошибка загрузки фото: 500',
      refetch: refetchMock,
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    expect(screen.getByText(/Ошибка загрузки фото: 500/)).toBeInTheDocument();

    // Нажимаем кнопку повтора
    const retryButton = screen.getByText('Повторить');
    await user.click(retryButton);

    // Проверяем, что refetch был вызван
    expect(refetchMock).toHaveBeenCalled();
  });

  /**
   * Проверяет отображение тегов фотографии.
   * Должен отображать все теги, если они есть в данных фотографии.
   */
  test('отображает теги если есть', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Природа')).toBeInTheDocument();
    expect(screen.getByText('Пейзаж')).toBeInTheDocument();
  });

  /**
   * Проверяет отсутствие раздела тегов при их отсутствии.
   * Не должен отображать раздел тегов если массив тегов пуст.
   */
  test('не отображает раздел тегов если нет тегов', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, tags: [] },
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('Тэги:')).not.toBeInTheDocument();
  });

  /**
   * Проверяет отображение EXIF данных фотографии.
   * Должен отображать информацию о камере и другие EXIF данные.
   */
  test('отображает EXIF данные если есть', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Информация')).toBeInTheDocument();
    expect(screen.getByText('Canon EOS 5D')).toBeInTheDocument();
  });

  /**
   * Проверяет отсутствие изображения при отсутствии URL.
   * Не должен отображать элемент img если image_url null.
   */
  test('не отображает изображение если нет image_url', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, image_url: null },
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет отсутствие описания при его отсутствии.
   * Не должен отображать описание если description null.
   */
  test('не отображает описание если нет description', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, description: null },
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('Описание фото')).not.toBeInTheDocument();
  });

  /**
   * Проверяет обработку фотографии без альбома.
   * Должен корректно обрабатывать случай, когда у фотографии нет альбома.
   */
  test('обрабатывает фото без альбома', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, album: null },
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    
    useAlbumPhotos.mockReturnValueOnce({
      photos: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
    expect(useAlbumPhotos).toHaveBeenCalledWith(null, '/api/gallery/photos/');
  });

  /**
   * Проверяет корректность навигационных ссылок.
   * Должен устанавливать правильные href для кнопок предыдущей и следующей фотографии.
   */
  test('навигация работает правильно', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: { id: 1, slug: 'photo-1' },
      nextPhoto: { id: 3, slug: 'photo-3' },
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    const prevButton = screen.getByText('← Предыдущая');
    const nextButton = screen.getByText('Следующая →');

    expect(prevButton).toHaveAttribute('href', '/gallery/photo/photo-1/');
    expect(nextButton).toHaveAttribute('href', '/gallery/photo/photo-3/');
  });

  /**
   * Проверяет обработку фотографии без даты съемки.
   * Должен корректно обрабатывать случай, когда у фотографии нет даты съемки.
   */
  test('обрабатывает фото без datetime_taken', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, datetime_taken: null },
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    
    useAlbumPhotos.mockReturnValueOnce({
      photos: [
        { id: 1, slug: 'photo-1', datetime_taken: null },
        { id: 2, slug: 'photo-2', datetime_taken: null },
        { id: 3, slug: 'photo-3', datetime_taken: null },
      ],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
  });

  /**
   * Проверяет отсутствие навигации для единственной фотографии в альбоме.
   * Не должен отображать кнопки навигации если в альбоме только одна фотография.
   */
  test('единственная фотография в альбоме не имеет навигации', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: null,
      nextPhoto: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('← Предыдущая')).not.toBeInTheDocument();
    expect(screen.queryByText('Следующая →')).not.toBeInTheDocument();
  });

  /**
   * Проверяет использование кастомного URL API.
   * Должен передавать кастомный apiUrl в хуки загрузки данных.
   */
  test('использует кастомный apiUrl', () => {
    render(<PhotoDetail photoSlug="test-photo" apiUrl="/custom/api/" />);
    expect(usePhotoData).toHaveBeenCalledWith('test-photo', '/custom/api/');
    expect(useAlbumPhotos).toHaveBeenCalledWith(1, '/custom/api/');
  });

  /**
   * Проверяет перезагрузку данных при изменении slug фотографии.
   * Должен вызывать хуки с новым photoSlug при изменении пропса.
   */
  test('перезагружает данные при изменении photoSlug', () => {
    const { rerender } = render(<PhotoDetail photoSlug="photo-1" />);
    expect(usePhotoData).toHaveBeenCalledWith('photo-1', '/api/gallery/photos/');
    rerender(<PhotoDetail photoSlug="photo-2" />);
    expect(usePhotoData).toHaveBeenCalledWith('photo-2', '/api/gallery/photos/');
  });

  /**
   * Проверяет обработку пустого массива фотографий альбома.
   * Должен корректно обрабатывать случай, когда в альбоме нет фотографий.
   */
  test('обрабатывает пустой массив albumPhotos', () => {
    useAlbumPhotos.mockReturnValueOnce({
      photos: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: null,
      nextPhoto: null,
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
    expect(screen.queryByText('← Предыдущая')).not.toBeInTheDocument();
  });

  /**
   * Проверяет обработку прямого массива фотографий без обертки results.
   * Должен корректно обрабатывать данные, полученные напрямую в виде массива.
   */
  test('обрабатывает прямой массив albumPhotos без results', () => {
    useAlbumPhotos.mockReturnValueOnce({
      photos: mockAlbumPhotos,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<PhotoDetail photoSlug="test-photo" />);

    expect(screen.getByText('← Предыдущая')).toBeInTheDocument();
  });

  /**
   * Проверяет обработку случая, когда фотография равна null.
   * Должен отображать сообщение "Фотография не найдена" если photo null.
   */
  test('обрабатывает случай когда photo null', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Фотография не найдена')).toBeInTheDocument();
  });

  /**
   * Проверяет обработку случая, когда фотография равна undefined.
   * Должен отображать сообщение "Фотография не найдена" если photo undefined.
   */
  test('обрабатывает случай когда photo undefined', () => {
    usePhotoData.mockReturnValueOnce({
      photo: undefined,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Фотография не найдена')).toBeInTheDocument();
  });
});
