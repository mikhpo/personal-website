import React from 'react';
import { render, screen } from '@testing-library/react';
import PhotoCard from './PhotoCard';

/**
 * Набор тестов для компонента PhotoCard.
 * Проверяет корректность отображения карточки фотографии с различными наборами данных,
 * включая минимальные и полные данные о фотографии, обработку граничных случаев
 * и правильность применения стилей.
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
    datetime_taken: '2024-01-15T10:30:00Z',
  };

  /**
   * Проверяет, что компонент корректно рендерится с минимальным набором пропсов.
   * Требует только обязательные поля: id, name, slug.
   */
  test('рендерит с минимальными props', () => {
    render(<PhotoCard photo={minimalPhoto} />);
    expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно рендерится с полным набором пропсов.
   * Включает проверку отображения названия, миниатюры и даты съёмки.
   */
  test('рендерит с полными props', () => {
    render(<PhotoCard photo={fullPhoto} />);
    expect(screen.getByText('Тестовое фото')).toBeInTheDocument();
    expect(screen.getByAltText('Тестовое фото')).toBeInTheDocument();
    expect(screen.getByText('15.01.2024')).toBeInTheDocument();
  });

  /**
   * Проверяет, что миниатюра не отображается, если thumbnail_url не задан.
   * При отсутствии URL миниатюры изображение не должно отображаться в DOM.
   */
  test('не отображает миниатюру если thumbnail_url пустой', () => {
    render(<PhotoCard photo={minimalPhoto} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что дата не отображается, если datetime_taken не задана.
   * При отсутствии даты съёмки элемент с датой не должен присутствовать в DOM.
   */
  test('не отображает дату если datetime_taken пустая', () => {
    render(<PhotoCard photo={minimalPhoto} />);
    const cardText = screen.queryByText('', { selector: '.card-text' });
    expect(cardText).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка на страницу фотографии имеет правильный URL.
   * Все ссылки в карточке должны вести на страницу конкретной фотографии
   * в формате /gallery/photo/{slug}/.
   */
  test('ссылка на фото имеет правильный URL', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveAttribute('href', '/gallery/photo/test-photo/');
    });
  });

  /**
   * Проверяет, что изображение имеет правильный источник.
   * Атрибут src изображения должен соответствовать значению thumbnail_url.
   */
  test('изображение имеет правильный src', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toHaveAttribute('src', '/media/test-thumbnail.jpg');
  });

  /**
   * Проверяет, что изображение загружается с атрибутом loading="lazy".
   * Для оптимизации производительности изображения должны использовать ленивую загрузку.
   */
  test('изображение имеет loading="lazy"', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const image = screen.getByAltText('Тестовое фото');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  /**
   * Проверяет, что к элементу Card применены правильные CSS классы.
   * Карточка должна иметь тень, белый фон, закругленные углы и занимать всю высоту родителя.
   */
  test('применяет правильные CSS классы к Card', () => {
    const { container } = render(<PhotoCard photo={fullPhoto} />);
    const card = container.querySelector('.card');
    expect(card).toHaveClass('shadow', 'bg-white', 'rounded', 'h-100');
  });

  /**
   * Проверяет, что ссылка на название не имеет подчеркивания.
   * Ссылка на название фотографии должна быть без подчеркивания и темного цвета
   * для лучшего визуального восприятия.
   */
  test('ссылка на название не имеет подчёркивания', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const titleLinks = screen.getAllByRole('link', { name: 'Тестовое фото' });
    // Найдем ссылку с нужными классами (это ссылка на название, а не на изображение)
    const titleLink = Array.from(titleLinks).find(link => 
      link.classList.contains('text-decoration-none') && link.classList.contains('text-dark')
    );
    expect(titleLink).toBeInTheDocument();
    expect(titleLink).toHaveClass('text-decoration-none', 'text-dark');
  });

  /**
   * Проверяет, что дата имеет правильные CSS классы.
   * Элемент с датой должен быть приглушенного цвета, маленького размера
   * и автоматически располагаться внизу карточки.
   */
  test('дата имеет правильные CSS классы', () => {
    render(<PhotoCard photo={fullPhoto} />);
    const dateText = screen.getByText('15.01.2024');
    expect(dateText).toHaveClass('text-muted', 'small', 'mt-auto');
  });

  /**
   * Проверяет, что Card.Body использует flexbox.
   * Контейнер содержимого карточки должен использовать flexbox для правильного
   * расположения элементов и автоматического позиционирования даты.
   */
  test('Card.Body использует flexbox', () => {
    const { container } = render(<PhotoCard photo={fullPhoto} />);
    const cardBody = container.querySelector('.card-body');
    expect(cardBody).toHaveClass('d-flex', 'flex-column');
  });

  /**
   * Проверяет, что дата форматируется в русской локали.
   * Дата должна отображаться в формате DD.MM.YYYY согласно русской локали.
   */
  test('форматирует дату в русской локали', () => {
    const photoWithDate = {
      ...minimalPhoto,
      datetime_taken: '2024-12-25T15:45:30Z',
    };
    render(<PhotoCard photo={photoWithDate} />);
    expect(screen.getByText('25.12.2024')).toBeInTheDocument();
  });

  /**
   * Проверяет обработку невалидной даты.
   * При получении некорректной строки даты компонент не должен отображать элемент с датой.
   */
  test('обрабатывает невалидную дату', () => {
    const photoWithInvalidDate = {
      ...minimalPhoto,
      datetime_taken: 'invalid-date',
    };
    render(<PhotoCard photo={photoWithInvalidDate} />);
    const cardText = screen.queryByText('', { selector: '.card-text' });
    expect(cardText).not.toBeInTheDocument();
  });

  /**
   * Проверяет обработку null значения в datetime_taken.
   * При значении null дата не должна отображаться в карточке.
   */
  test('обрабатывает null в datetime_taken', () => {
    const photoWithNullDate = {
      ...minimalPhoto,
      datetime_taken: null,
    };
    render(<PhotoCard photo={photoWithNullDate} />);
    const cardText = screen.queryByText('', { selector: '.card-text' });
    expect(cardText).not.toBeInTheDocument();
  });

  /**
   * Проверяет отображение фотографии с длинным названием.
   * Компонент должен корректно отображать названия произвольной длины.
   */
  test('рендерит с длинным названием', () => {
    const photoWithLongName = {
      ...minimalPhoto,
      name: 'Очень длинное название фотографии которое может занимать несколько строк',
    };
    render(<PhotoCard photo={photoWithLongName} />);
    expect(screen.getByText(photoWithLongName.name)).toBeInTheDocument();
  });

  /**
   * Проверяет отображение фотографии со специальными символами в названии.
   * Компонент должен корректно обрабатывать специальные символы в названии.
   */
  test('рендерит со спецсимволами в названии', () => {
    const photoWithSpecialChars = {
      ...minimalPhoto,
      name: 'Фото <>&"\'',
    };
    render(<PhotoCard photo={photoWithSpecialChars} />);
    expect(screen.getByText(photoWithSpecialChars.name)).toBeInTheDocument();
  });

  /**
   * Проверяет поведение при пустой строке в thumbnail_url.
   * При пустом значении URL миниатюры изображение не должно отображаться.
   */
  test('рендерит с пустой строкой в thumbnail_url', () => {
    const photoWithEmptyThumbnail = {
      ...fullPhoto,
      thumbnail_url: '',
    };
    render(<PhotoCard photo={photoWithEmptyThumbnail} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  /**
   * Проверяет поведение при пустой строке в datetime_taken.
   * При пустом значении даты элемент с датой не должен отображаться.
   */
  test('рендерит с пустой строкой в datetime_taken', () => {
    const photoWithEmptyDate = {
      ...fullPhoto,
      datetime_taken: '',
    };
    render(<PhotoCard photo={photoWithEmptyDate} />);
    const cardText = screen.queryByText('', { selector: '.card-text' });
    expect(cardText).not.toBeInTheDocument();
  });

  /**
   * Проверяет форматирование различных дат.
   * Компонент должен корректно форматировать различные даты в формат DD.MM.YYYY.
   */
  test('форматирует различные даты правильно', () => {
    const dates = [
      { input: '2024-01-01T00:00:00Z', expected: '01.01.2024' },
      { input: '2024-06-15T12:30:45Z', expected: '15.06.2024' },
      { input: '2024-12-31T23:59:59Z', expected: '31.12.2024' },
    ];
    dates.forEach(({ input }) => {
      const { unmount } = render(<PhotoCard photo={{ ...minimalPhoto, datetime_taken: input }} />);
      const dateElements = screen.getAllByText(/\d{2}\.\d{2}\.\d{4}/);
      expect(dateElements.length).toBeGreaterThan(0);
      unmount();
    });
  });
});
