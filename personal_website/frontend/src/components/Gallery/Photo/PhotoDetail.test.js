import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoDetail from './PhotoDetail/PhotoDetail';

jest.mock('./PhotoDetail/hooks/usePhotoData');
jest.mock('./PhotoDetail/hooks/useAlbumPhotos');
jest.mock('./PhotoDetail/hooks/usePhotoNavigation');

import usePhotoData from './PhotoDetail/hooks/usePhotoData';
import useAlbumPhotos from './PhotoDetail/hooks/useAlbumPhotos';
import usePhotoNavigation from './PhotoDetail/hooks/usePhotoNavigation';

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
    });
    
    useAlbumPhotos.mockReturnValue({
      photos: mockAlbumPhotos,
      loading: false,
      error: null,
    });
    
    usePhotoNavigation.mockReturnValue({
      previousPhoto: mockPreviousPhoto,
      nextPhoto: mockNextPhoto,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('отображает изображение фотографии', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/media/photo.jpg');
  });

  test('отображает кнопки навигации', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('<')).toBeInTheDocument();
    expect(screen.getByText('>')).toBeInTheDocument();
    expect(screen.getByText('О фото')).toBeInTheDocument();
  });

  test('отображает кнопку "О фото" для открытия EXIF модального окна', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('О фото')).toBeInTheDocument();
  });

  test('отображает индикатор загрузки', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: true,
      error: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Загрузка фотографии...')).toBeInTheDocument();
  });

  test('отображает ошибку загрузки', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: 'Ошибка загрузки фото: 404',
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Ошибка загрузки фото: 404')).toBeInTheDocument();
  });

  test('отображает сообщение если фото не найдено', () => {
    usePhotoData.mockReturnValueOnce({
      photo: null,
      loading: false,
      error: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.getByText('Фотография не найдена')).toBeInTheDocument();
  });

  test('нет кнопки "Предыдущая" если previousPhoto null', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: null,
      nextPhoto: mockNextPhoto,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('<')).not.toBeInTheDocument();
  });

  test('нет кнопки "Следующая" если nextPhoto null', () => {
    usePhotoNavigation.mockReturnValueOnce({
      previousPhoto: mockPreviousPhoto,
      nextPhoto: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByText('>')).not.toBeInTheDocument();
  });

  test('ссылка на предыдущую фотографию имеет правильный href', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    const prevLink = screen.getByText('<');
    expect(prevLink).toHaveAttribute('href', '/gallery/photo/photo-1/');
  });

  test('ссылка на следующую фотографию имеет правильный href', () => {
    render(<PhotoDetail photoSlug="test-photo" />);
    const nextLink = screen.getByText('>');
    expect(nextLink).toHaveAttribute('href', '/gallery/photo/photo-3/');
  });

  test('открывает модальное окно EXIF при нажатии на кнопку "О фото"', async () => {
    const user = userEvent.setup();
    render(<PhotoDetail photoSlug="test-photo" />);
    
    const exifButton = screen.getByText('О фото');
    await user.click(exifButton);
    
    expect(await screen.findByText('EXIF')).toBeInTheDocument();
    expect(await screen.findByText('Камера')).toBeInTheDocument();
    expect(await screen.findByText('Canon EOS 5D')).toBeInTheDocument();
  });

  test('закрывает модальное окно EXIF при нажатии на кнопку закрытия', async () => {
    const user = userEvent.setup();
    render(<PhotoDetail photoSlug="test-photo" />);
    
    const exifButton = screen.getByText('О фото');
    await user.click(exifButton);
    
    const closeButton = await screen.findByText('Закрыть');
    await user.click(closeButton);
    
    expect(screen.queryByText('EXIF')).not.toBeInTheDocument();
  });

  test('не отображает изображение если нет image_url', () => {
    usePhotoData.mockReturnValueOnce({
      photo: { ...mockPhoto, image_url: null },
      loading: false,
      error: null,
    });
    render(<PhotoDetail photoSlug="test-photo" />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });
});
