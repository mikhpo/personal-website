import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoDetail from './PhotoDetail';

jest.mock('@hooks/usePhotoData');
jest.mock('@services/navigation');

import { usePhotoData } from '@hooks';
import { navigateTo } from '@services';

/**
 * Набор тестов для компонента PhotoDetail.
 *
 * Проверяет отображение фотографии, навигацию между фотографиями,
 * состояния загрузки и ошибок, а также работу модального окна EXIF.
 */
describe('PhotoDetail', () => {
  const mockPhoto = {
    id: 2,
    name: 'Тестовое фото',
    slug: 'test-photo',
    image_url: '/media/photo.jpg',
    album: 1,
    camera: 'Canon EOS 5D',
    lens_model: 'Canon EF 24-70mm',
    aperture: 'f/2.8',
    exposure: '1/125',
    iso: 400,
    focal_length: 50,
    datetime_taken: '2024-01-15T10:00:00Z',
  };

  // ID соседних фотографий для навигации (mockPhoto имеет id=2)
  const mockPreviousPhotoId = 1; // Предыдущая фотография в альбоме
  const mockNextPhotoId = 3; // Следующая фотография в альбомe

  // Настройка: изолируем тесты от реальных API запросов
  // PhotoDetail использует хук usePhotoData для загрузки данных
  beforeEach(() => {
    usePhotoData.mockReturnValue({
      photo: mockPhoto,
      loading: false,
      error: null,
    });
    navigateTo.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверяет, что компонент отображает изображение фотографии
   * с правильным alt-текстом и src-адресом.
   */
  test('отображает изображение фотографии', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/media/photo.jpg');
  });

  /**
   * Проверяет, что компонент отображает кнопки навигации:
   * "Предыдущая" (<), "Следующая" (>) и "О фото".
   */
  test('отображает кнопки навигации', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);
    expect(screen.getByText('<')).toBeInTheDocument();
    expect(screen.getByText('>')).toBeInTheDocument();
    expect(screen.getByText('О фото')).toBeInTheDocument();
  });

  /**
   * Проверяет, что кнопка "О фото" присутствует в DOM
   * и предназначена для открытия модального окна с EXIF-данными.
   */
  test('отображает кнопку "О фото" для открытия EXIF модального окна', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);
    expect(screen.getByText('О фото')).toBeInTheDocument();
  });

  /**
   * Проверяет, что во время загрузки данных отображается
   * индикатор загрузки с соответствующим сообщением.
   */
  test('отображает индикатор загрузки', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: true,
      error: null,
    });
    render(<PhotoDetail photoId={2} />);
    expect(screen.getByText('Загрузка фотографии...')).toBeInTheDocument();
  });

  /**
   * Проверяет, что при ошибке загрузки данных отображается
   * сообщение об ошибке с переданным текстом.
   */
  test('отображает ошибку загрузки', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: 'Ошибка загрузки фото: 404',
    });
    render(<PhotoDetail photoId={2} />);
    expect(screen.getByText('Ошибка загрузки фото: 404')).toBeInTheDocument();
  });

  /**
   * Проверяет, что если фотография не найдена (photo === null без ошибки),
   * отображается соответствующее сообщение.
   */
  test('отображает сообщение если фото не найдено', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: null,
    });
    render(<PhotoDetail photoId={2} />);
    expect(screen.getByText('Фотография не найдена')).toBeInTheDocument();
  });

  /**
   * Проверяет, что кнопка "Предыдущая" не отображается,
   * если previousPhotoId равен null.
   */
  test('нет кнопки "Предыдущая" если previousPhotoId null', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={null} nextPhotoId={mockNextPhotoId} />);
    expect(screen.queryByText('<')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что кнопка "Следующая" не отображается,
   * если nextPhotoId равен null.
   */
  test('нет кнопки "Следующая" если nextPhotoId null', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={null} />);
    expect(screen.queryByText('>')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на предыдущую фотографию ведёт
   * на правильный URL вида /gallery/photo/{id}/.
   */
  test('ссылка на предыдущую фотографию имеет правильный href', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);
    const prevLink = screen.getByText('<');
    expect(prevLink).toHaveAttribute('href', '/gallery/photo/1/');
  });

  /**
   * Проверяет, что ссылка на следующую фотографию ведёт
   * на правильный URL вида /gallery/photo/{id}/.
   */
  test('ссылка на следующую фотографию имеет правильный href', () => {
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);
    const nextLink = screen.getByText('>');
    expect(nextLink).toHaveAttribute('href', '/gallery/photo/3/');
  });

  /**
   * Проверяет, что при нажатии на кнопку "О фото" открывается
   * модальное окно с EXIF-данными: заголовок "EXIF", поле "Камера"
   * и значение "Canon EOS 5D".
   */
  test('открывает модальное окно EXIF при нажатии на кнопку "О фото"', async () => {
    const user = userEvent.setup();
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

    const exifButton = screen.getByText('О фото');
    await user.click(exifButton);

    expect(await screen.findByText('EXIF')).toBeInTheDocument();
    expect(await screen.findByText('Камера')).toBeInTheDocument();
    expect(await screen.findByText('Canon EOS 5D')).toBeInTheDocument();
  });

  /**
   * Проверяет, что модальное окно EXIF закрывается при нажатии
   * на кнопку "Закрыть" - заголовок "EXIF" исчезает из DOM.
   */
  test('закрывает модальное окно EXIF при нажатии на кнопку закрытия', async () => {
    const user = userEvent.setup();
    render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

    const exifButton = screen.getByText('О фото');
    await user.click(exifButton);

    const closeButton = await screen.findByText('Закрыть');
    await user.click(closeButton);

    expect(screen.queryByText('EXIF')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что если у фотографии отсутствует image_url,
   * элемент img не рендерится.
   */
  test('не отображает изображение если нет image_url', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, image_url: null },
      loading: false,
      error: null,
    });
    render(<PhotoDetail photoId={2} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет переключение фотографий клавиатурой и свайпами.
   * Навигация выполняется полной загрузкой страницы через сервис navigateTo.
   */
  describe('навигация клавиатурой и свайпами', () => {
    /**
     * Проверяет, что клавиша ArrowRight переключает
     * на следующую фотографию альбома.
     */
    test('ArrowRight переходит к следующей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith('/gallery/photo/3/');
    });

    /**
     * Проверяет, что клавиша ArrowLeft переключает
     * на предыдущую фотографию альбома.
     */
    test('ArrowLeft переходит к предыдущей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

      fireEvent.keyDown(document, { key: 'ArrowLeft' });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith('/gallery/photo/1/');
    });

    /**
     * Проверяет, что свайп влево переключает на следующую фотографию.
     */
    test('свайп влево переходит к следующей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith('/gallery/photo/3/');
    });

    /**
     * Проверяет, что свайп вправо переключает на предыдущую фотографию.
     */
    test('свайп вправо переходит к предыдущей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

      fireEvent.touchStart(document, { touches: [{ clientX: 100, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 220, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith('/gallery/photo/1/');
    });

    /**
     * Проверяет, что при открытом модальном окне EXIF
     * клавиатурная навигация отключена.
     */
    test('стрелки игнорируются при открытом модальном окне EXIF', async () => {
      const user = userEvent.setup();
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={mockNextPhotoId} />);

      await user.click(screen.getByText('О фото'));
      expect(await screen.findByText('EXIF')).toBeInTheDocument();

      fireEvent.keyDown(document, { key: 'ArrowLeft' });
      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).not.toHaveBeenCalled();

      await user.click(await screen.findByText('Закрыть'));

      // После закрытия окна навигация снова работает.
      fireEvent.keyDown(document, { key: 'ArrowRight' });
      expect(navigateTo).toHaveBeenCalledWith('/gallery/photo/3/');
    });

    /**
     * Проверяет, что без предыдущей фотографии клавиша ArrowLeft
     * не выполняет переход.
     */
    test('ArrowLeft игнорируется без предыдущей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={null} nextPhotoId={mockNextPhotoId} />);

      fireEvent.keyDown(document, { key: 'ArrowLeft' });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    /**
     * Проверяет, что без следующей фотографии клавиша ArrowRight
     * не выполняет переход.
     */
    test('ArrowRight игнорируется без следующей фотографии', () => {
      render(<PhotoDetail photoId={2} previousPhotoId={mockPreviousPhotoId} nextPhotoId={null} />);

      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).not.toHaveBeenCalled();
    });
  });
});
