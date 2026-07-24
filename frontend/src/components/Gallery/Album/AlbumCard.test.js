/**
 * Тесты для компонента AlbumCard.
 *
 * Проверяет корректность отображения карточки альбома с различными наборами данных,
 * включая минимальные и полные данные альбома, обработку пустых значений,
 * правильность ссылок и изображений.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import AlbumCard from '@components/Gallery/Album/AlbumCard';

describe('AlbumCard', () => {
  const minimalAlbum = {
    id: 1,
    name: 'Тестовый альбом',
    slug: 'test-album',
  };

  const fullAlbum = {
    id: 1,
    name: 'Тестовый альбом',
    slug: 'test-album',
    description: 'Описание тестового альбома',
    cover_thumbnail_url: '/media/test-cover.jpg',
  };

  /**
   * Проверяет, что компонент корректно рендерится с минимальным набором свойств.
   * Должно отображаться название альбома.
   */
  test('рендерит с минимальными props', () => {
    render(<AlbumCard album={minimalAlbum} />);
    expect(screen.getByText('Тестовый альбом')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно рендерится с полным набором свойств.
   * Должны отображаться название и обложка альбома.
   */
  test('рендерит с полными props', () => {
    render(<AlbumCard album={fullAlbum} />);
    expect(screen.getByText('Тестовый альбом')).toBeInTheDocument();
    expect(screen.getByAltText('Тестовый альбом')).toBeInTheDocument();
  });

  /**
   * Проверяет, что обложка не отображается, если URL миниатюры пустой.
   * Компонент должен корректно обрабатывать отсутствие изображения.
   */
  test('не отображает обложку если cover_thumbnail_url пустой', () => {
    render(<AlbumCard album={minimalAlbum} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });


  /**
   * Проверяет, что ссылка на альбом формируется с правильным URL.
   * Все ссылки в карточке должны вести на страницу альбома.
   */
  test('ссылка на альбом имеет правильный URL', () => {
    render(<AlbumCard album={fullAlbum} />);
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveAttribute('href', '/gallery/album/1/');
    });
  });

  /**
   * Проверяет, что изображение обложки имеет правильный источник.
   * Атрибут src изображения должен соответствовать URL из данных альбома.
   */
  test('изображение имеет правильный src', () => {
    render(<AlbumCard album={fullAlbum} />);
    const image = screen.getByAltText('Тестовый альбом');
    expect(image).toHaveAttribute('src', '/media/test-cover.jpg');
  });

  /**
   * Проверяет, что изображение загружается с атрибутом lazy loading.
   * Оптимизация производительности путем отложенной загрузки изображений.
   */
  test('изображение имеет loading="lazy"', () => {
    render(<AlbumCard album={fullAlbum} />);
    const image = screen.getByAltText('Тестовый альбом');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  /**
   * Проверяет применение правильных CSS классов к элементу Card.
   * Компонент должен иметь стандартные стили оформления карточки.
   */
  test('применяет правильные CSS классы к Card', () => {
    const renderResult = render(<AlbumCard album={fullAlbum} />);
    const card = renderResult.container.querySelector('.card');
    expect(card).toHaveClass('shadow', 'bg-white', 'rounded', 'text-center', 'h-100');
  });

  /**
   * Проверяет, что ссылка на название альбома не имеет подчеркивания.
   * В компоненте есть две ссылки с одинаковым текстом "Тестовый альбом":
   * 1. Ссылка на обложку (изображение) - без дополнительных CSS классов
   * 2. Ссылка на название альбома - с классами text-decoration-none и text-dark
   * Тест находит именно вторую ссылку по наличию этих классов.
   */
  test('ссылка на название не имеет подчёркивания', () => {
    render(<AlbumCard album={fullAlbum} />);
    // Получаем все ссылки с текстом "Тестовый альбом"
    const titleLinks = screen.getAllByRole('link', { name: 'Тестовый альбом' });
    // Найдем ссылку с нужными классами (это ссылка на название, а не на изображение)
    const titleLink = Array.from(titleLinks).find(link =>
      link.classList.contains('text-decoration-none') && link.classList.contains('text-dark')
    );
    expect(titleLink).toBeInTheDocument();
    expect(titleLink).toHaveClass('text-decoration-none', 'text-dark');
  });

  /**
   * Проверяет, что тело карточки использует flexbox для выравнивания.
   * Элемент Card.Body должен использовать flexbox для корректного расположения содержимого.
   */
  test('Card.Body использует flexbox', () => {
    const renderResult = render(<AlbumCard album={fullAlbum} />);
    const cardBody = renderResult.container.querySelector('.card-body');
    expect(cardBody).toHaveClass('d-flex', 'flex-column');
  });

  /**
   * Проверяет корректность отображения альбома с длинным названием.
   * Компонент должен корректно отображать названия произвольной длины.
   */
  test('рендерит с длинным названием', () => {
    const albumWithLongName = {
      ...minimalAlbum,
      name: 'Очень длинное название альбома которое может занимать несколько строк',
    };
    render(<AlbumCard album={albumWithLongName} />);
    expect(screen.getByText(albumWithLongName.name)).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения специальных символов в названии.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в названии', () => {
    const albumWithSpecialChars = {
      ...minimalAlbum,
      name: 'Альбом <>&"\'',
    };
    render(<AlbumCard album={albumWithSpecialChars} />);
    expect(screen.getByText(albumWithSpecialChars.name)).toBeInTheDocument();
  });

  /**
   * Проверяет поведение компонента при пустом URL обложки.
   * При пустом значении cover_thumbnail_url изображение не должно отображаться.
   */
  test('рендерит с пустой строкой в cover_thumbnail_url', () => {
    const albumWithEmptyCover = {
      ...fullAlbum,
      cover_thumbnail_url: '',
    };
    render(<AlbumCard album={albumWithEmptyCover} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });
});
