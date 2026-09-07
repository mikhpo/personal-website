import React from 'react';
import { render, screen } from '@testing-library/react';
import AboutPhoto from './AboutPhoto';

/**
 * Тесты для компонента AboutPhoto
 *
 * Проверяет объединение информации о фотографии: ссылку на альбом,
 * описание и таблицу EXIF данных, а также скрытие пустых блоков.
 */
describe('AboutPhoto', () => {
  const fullPhoto = {
    album: 3,
    album_name: 'Путешествия',
    description: 'Описание тестовой фотографии',
    camera: 'Canon EOS 5D Mark IV',
    lens_model: 'Canon EF 24-70mm f/2.8L II USM',
    aperture: 'f/2.8',
    exposure: '1/125',
    iso: 400,
    focal_length: 50,
    datetime_taken: '2024-01-15T10:30:00Z',
  };

  /**
   * Проверяет, что название альбома отображается ссылкой
   * на страницу детального просмотра альбома
   */
  test('рендерит ссылку на страницу альбома', () => {
    render(<AboutPhoto photo={fullPhoto} />);
    const albumLink = screen.getByText('Путешествия');
    expect(albumLink).toHaveAttribute('href', '/gallery/album/3/');
    expect(albumLink.tagName).toBe('A');
  });

  /**
   * Проверяет, что строка альбома не отображается, если album_name отсутствует
   */
  test('не рендерит альбом без album_name', () => {
    const photoWithoutAlbum = { ...fullPhoto, album: undefined, album_name: undefined };
    render(<AboutPhoto photo={photoWithoutAlbum} />);
    expect(screen.queryByText('Путешествия')).not.toBeInTheDocument();
  });

  /**
   * Проверяет отображение описания фотографии
   */
  test('рендерит описание фотографии', () => {
    render(<AboutPhoto photo={fullPhoto} />);
    expect(screen.getByText('Описание тестовой фотографии')).toBeInTheDocument();
  });

  /**
   * Проверяет, что абзац описания не отображается без description
   */
  test('не рендерит описание без description', () => {
    const photoWithoutDescription = { ...fullPhoto, description: undefined };
    render(<AboutPhoto photo={photoWithoutDescription} />);
    expect(screen.queryByText('Описание тестовой фотографии')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент отображает таблицу EXIF данных
   */
  test('рендерит EXIF данные', () => {
    render(<AboutPhoto photo={fullPhoto} />);
    expect(screen.getByText('Камера')).toBeInTheDocument();
    expect(screen.getByText('Canon EOS 5D Mark IV')).toBeInTheDocument();
    expect(screen.getByText('Дата съёмки')).toBeInTheDocument();
  });

  /**
   * Проверяет, что без EXIF данных таблица не отображается,
   * даже если заполнены альбом и описание
   */
  test('не рендерит EXIF таблицу без данных', () => {
    const photoWithoutExif = {
      album: 3,
      album_name: 'Путешествия',
      description: 'Описание тестовой фотографии',
    };
    render(<AboutPhoto photo={photoWithoutExif} />);
    expect(screen.queryByText('Камера')).not.toBeInTheDocument();
    expect(screen.getByText('Путешествия')).toBeInTheDocument();
  });

  /**
   * Проверяет, что без альбома, описания и EXIF данных
   * компонент не отображает никакого содержимого
   */
  test('не рендерит ничего без данных', () => {
    const { container } = render(<AboutPhoto photo={{}} />);
    expect(container.firstChild).toBeNull();
  });
});
