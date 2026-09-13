import React from 'react';
import { render, screen } from '@testing-library/react';
import PhotoCard from './PhotoCard';

/**
 * Набор тестов для компонента PhotoCard.
 * Проверяет корректность отображения карточки фотографии в соответствии
 * со старой Django-реализацией (только изображение без текста).
 */
describe('PhotoCard', () => {
  const minimalPhoto = {
    id: 1,
    name: 'Тестовое фото',
    slug: 'test-photo',
  };

  const fullPhoto = {
    id: 1,
    name: 'Тестовое фото',
    slug: 'test-photo',
    thumbnail_url: '/media/test-thumbnail.jpg',
  };

  /**
   * Проверяет, что компонент корректно рендерится с минимальным набором пропсов.
   * В старой реализации карточка содержит только изображение.
   */
  test('рендерит с минимальными props', () => {
    render(<PhotoCard photo={minimalPhoto} />);
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/gallery/photo/1/');
  });

  /**
   * Проверяет, что компонент корректно рендерится с полным набором пропсов.
   * Включает проверку отображения миниатюры.
   */
  test('рендерит с полными props', () => {
    render(<PhotoCard photo={fullPhoto} />);
    expect(screen.getByAltText('Тестовое фото')).toBeInTheDocument();
  });

  /**
   * Проверяет, что миниатюра не отображается, если thumbnail_url не задан.
   */
  test('не отображает миниатюру если thumbnail_url пустой', () => {
    render(<PhotoCard photo={minimalPhoto} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на страницу фотографии имеет правильный URL.
   */
  test('ссылка на фото имеет правильный URL', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveAttribute('href', '/gallery/photo/1/');
    });
  });

  /**
   * Проверяет, что изображение имеет правильный источник.
   */
  test('изображение имеет правильный src', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toHaveAttribute('src', '/media/test-thumbnail.jpg');
  });

  /**
   * Проверяет, что изображение загружается с атрибутом loading="lazy".
   */
  test('изображение имеет loading="lazy"', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  /**
   * Проверяет, что к элементу Card применены правильные CSS классы.
   */
  test('применяет правильные CSS классы к Card', () => {
    const { container } = render(<PhotoCard photo={fullPhoto} />);
    const card = container.querySelector('.card');
    expect(card).toHaveClass('shadow', 'rounded', 'text-center');
  });

  /**
   * Проверяет, что изображение имеет класс card-img как в старой реализации.
   */
  test('изображение имеет класс card-img', () => {
    const { container } = render(<PhotoCard photo={fullPhoto} />);
    const img = container.querySelector('img');
    expect(img).toHaveClass('card-img');
  });

  /**
   * Проверяет поведение при пустой строке в thumbnail_url.
   */
  test('рендерит с пустой строкой в thumbnail_url', () => {
    const photoWithEmptyThumbnail = {
      ...fullPhoto,
      thumbnail_url: '',
    };
    render(<PhotoCard photo={photoWithEmptyThumbnail} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });
});
