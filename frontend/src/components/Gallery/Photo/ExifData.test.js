import React from 'react';
import { render, screen } from '@testing-library/react';
import ExifData from './ExifData';

/**
 * Тесты для компонента ExifData
 *
 * Проверяет корректность отображения EXIF данных фотографии,
 * включая форматирование значений и обработку граничных случаев.
 */
describe('ExifData', () => {
  const emptyPhoto = {};

  const fullPhoto = {
    camera: 'Canon EOS 5D Mark IV',
    lens_model: 'Canon EF 24-70mm f/2.8L II USM',
    aperture: 'f/2.8',
    exposure: '1/125',
    iso: 400,
    focal_length: 50,
    datetime_taken: '2024-01-15T10:30:00Z',
  };

  /**
   * Проверяет, что компонент возвращает null, когда все поля фото пустые
   */
  test('возвращает null если все поля пустые', () => {
    const { container } = render(<ExifData photo={emptyPhoto} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент корректно рендерит таблицу со всеми EXIF данными
   */
  test('рендерит таблицу с полными EXIF данными', () => {
    render(<ExifData photo={fullPhoto} />);
    expect(screen.getByText('Камера')).toBeInTheDocument();
    expect(screen.getByText('Canon EOS 5D Mark IV')).toBeInTheDocument();
    expect(screen.getByText('Объектив')).toBeInTheDocument();
    expect(screen.getByText('Canon EF 24-70mm f/2.8L II USM')).toBeInTheDocument();
    expect(screen.getByText('Диафрагма')).toBeInTheDocument();
    expect(screen.getByText('f/2.8')).toBeInTheDocument();
    expect(screen.getByText('Выдержка')).toBeInTheDocument();
    expect(screen.getByText('1/125 с')).toBeInTheDocument();
    expect(screen.getByText('ISO')).toBeInTheDocument();
    expect(screen.getByText('ISO 400')).toBeInTheDocument();
    expect(screen.getByText('Фокусное расстояние')).toBeInTheDocument();
    expect(screen.getByText('50 мм')).toBeInTheDocument();
    expect(screen.getByText('Дата съёмки')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент рендерит только заполненные поля EXIF данных
   */
  test('рендерит только заполненные поля', () => {
    const partialPhoto = {
      camera: 'Nikon D850',
      iso: 800,
    };
    render(<ExifData photo={partialPhoto} />);
    expect(screen.getByText('Камера')).toBeInTheDocument();
    expect(screen.getByText('Nikon D850')).toBeInTheDocument();
    expect(screen.getByText('ISO')).toBeInTheDocument();
    expect(screen.getByText('ISO 800')).toBeInTheDocument();
    expect(screen.queryByText('Объектив')).not.toBeInTheDocument();
    expect(screen.queryByText('Диафрагма')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что к значению выдержки добавляется суффикс " с"
   */
  test('добавляет суффикс " с" к выдержке', () => {
    const photoWithExposure = { exposure: '1/1000' };
    render(<ExifData photo={photoWithExposure} />);
    expect(screen.getByText('1/1000 с')).toBeInTheDocument();
  });

  /**
   * Проверяет, что к значению ISO добавляется префикс "ISO "
   */
  test('добавляет префикс "ISO " к ISO', () => {
    const photoWithIso = { iso: 1600 };
    render(<ExifData photo={photoWithIso} />);
    expect(screen.getByText('ISO 1600')).toBeInTheDocument();
  });

  /**
   * Проверяет, что к значению фокусного расстояния добавляется суффикс " мм"
   */
  test('добавляет суффикс " мм" к фокусному расстоянию', () => {
    const photoWithFocalLength = { focal_length: 85 };
    render(<ExifData photo={photoWithFocalLength} />);
    expect(screen.getByText('85 мм')).toBeInTheDocument();
  });

  /**
   * Проверяет, что дата форматируется в русской локали
   */
  test('форматирует дату в русской локали', () => {
    const photoWithDate = { datetime_taken: '2024-12-25T15:45:30Z' };
    render(<ExifData photo={photoWithDate} />);
    const dateText = screen.getByText(/25\.12\.2024/);
    expect(dateText).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент возвращает null при некорректной дате
   */
  test('обрабатывает невалидную дату', () => {
    const photoWithInvalidDate = { datetime_taken: 'invalid-date' };
    const { container } = render(<ExifData photo={photoWithInvalidDate} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что таблица содержит правильное количество строк
   */
  test('рендерит правильное количество строк', () => {
    const { container } = render(<ExifData photo={fullPhoto} />);

    const rows = container.querySelectorAll('tbody tr');
    expect(rows).toHaveLength(7);
  });

  /**
   * Проверяет, что компонент возвращает null при ISO равном 0
   */
  test('обрабатывает ISO 0', () => {
    const photoWithZeroIso = { iso: 0 };
    const { container } = render(<ExifData photo={photoWithZeroIso} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null при focal_length равном 0
   */
  test('обрабатывает focal_length 0', () => {
    const photoWithZeroFocalLength = { focal_length: 0 };
    const { container } = render(<ExifData photo={photoWithZeroFocalLength} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null при пустых строковых значениях
   */
  test('обрабатывает пустые строки', () => {
    const photoWithEmptyStrings = {
      camera: '',
      lens_model: '',
      aperture: '',
      exposure: '',
    };
    const { container } = render(<ExifData photo={photoWithEmptyStrings} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null при null значениях всех полей
   */
  test('рендерит с null значениями', () => {
    const photoWithNulls = {
      camera: null,
      lens_model: null,
      aperture: null,
      exposure: null,
      iso: null,
      focal_length: null,
      datetime_taken: null,
    };
    const { container } = render(<ExifData photo={photoWithNulls} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент корректно обрабатывает спецсимволы в текстовых полях
   */
  test('рендерит со спецсимволами в текстовых полях', () => {
    const photoWithSpecialChars = {
      camera: 'Canon <>&"\'',
      lens_model: 'Lens <>&"\'',
    };
    render(<ExifData photo={photoWithSpecialChars} />);
    expect(screen.getByText('Canon <>&"\'')).toBeInTheDocument();
    expect(screen.getByText('Lens <>&"\'')).toBeInTheDocument();
  });
});
