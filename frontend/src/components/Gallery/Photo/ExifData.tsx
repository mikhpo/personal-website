import React from 'react';
import { Table } from 'react-bootstrap';
import type { components } from '../../../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Свойства компонента EXIF данных. */
export interface ExifDataProps {
  /** Объект фотографии с EXIF данными. */
  photo: Photo;
}

/** Строка таблицы EXIF данных. */
interface ExifField {
  label: string;
  value: string | number | null;
}

/**
 * Компонент для отображения EXIF данных фотографии.
 *
 * Отображает технические параметры съёмки в форматированной таблице.
 * Компонент автоматически скрывает пустые поля и возвращает null,
 * если нет данных для отображения.
 */
const ExifData = ({ photo }: ExifDataProps) => {
  /**
   * Форматирует строку даты в локализованный формат времени.
   *
   * @example
   * formatDateTime('2024-01-15T10:30:00Z') // '15.01.2024, 13:30:00'
   */
  const formatDateTime = (dateString: string | null | undefined): string | null => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return null;
      return date.toLocaleString('ru-RU');
    } catch {
      return null;
    }
  };

  const exifFields: ExifField[] = [
    { label: 'Камера', value: photo.camera },
    { label: 'Объектив', value: photo.lens_model },
    { label: 'Диафрагма', value: photo.aperture },
    { label: 'Выдержка', value: photo.exposure ? `${photo.exposure} с` : null },
    { label: 'ISO', value: photo.iso ? `ISO ${photo.iso}` : null },
    { label: 'Фокусное расстояние', value: photo.focal_length ? `${photo.focal_length} мм` : null },
    { label: 'Дата съёмки', value: formatDateTime(photo.taken_at) },
  ];

  const filledFields = exifFields.filter((field) => field.value);

  if (filledFields.length === 0) {
    return null;
  }

  return (
    <Table striped bordered size="sm" className="mb-0">
      <tbody>
        {filledFields.map((field) => (
          <tr key={field.label}>
            <td className="fw-bold" style={{ width: '40%' }}>
              {field.label}
            </td>
            <td>{field.value}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ExifData;
