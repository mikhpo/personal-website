import React from 'react';
import { Table } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент для отображения EXIF данных фотографии.
 *
 * Отображает технические параметры съёмки в форматированной таблице.
 * Компонент автоматически скрывает пустые поля и возвращает null,
 * если нет данных для отображения.
 *
 * @component
 * @param {Object} props - Свойства компонента
 * @param {Object} props.photo - Объект фотографии с EXIF данными
 * @param {string} [props.photo.camera] - Название камеры (производитель и модель)
 * @param {string} [props.photo.lens_model] - Модель объектива
 * @param {string} [props.photo.aperture] - Диафрагма (например, f/2.8)
 * @param {string} [props.photo.exposure] - Выдержка (например, 1/125)
 * @param {number} [props.photo.iso] - Чувствительность ISO
 * @param {number} [props.photo.focal_length] - Фокусное расстояние в мм
 * @param {string} [props.photo.datetime_taken] - Дата и время съёмки в формате ISO
 * @return {JSX.Element|null} Таблица с EXIF данными или null, если данные отсутствуют
 *
 * @example
 * // Пример использования компонента
 * const photo = {
 *   camera: 'Canon EOS 5D Mark IV',
 *   lens_model: 'EF 24-70mm f/2.8L II USM',
 *   aperture: 'f/2.8',
 *   exposure: '1/125',
 *   iso: 400,
 *   focal_length: 50,
 *   datetime_taken: '2024-01-15T10:30:00Z'
 * };
 *
 * return <ExifData photo={photo} />;
 */
const ExifData = ({ photo }) => {
  /**
   * Форматирует строку даты в локализованный формат времени
   * @param {string|null} dateString - Строка даты в формате ISO 8601
   * @return {string|null} Отформатированная дата в русской локали или null при ошибке
   * @example
   * // Возвращает дату в формате DD.MM.YYYY, HH:MM:SS
   * formatDateTime('2024-01-15T10:30:00Z') // '15.01.2024, 13:30:00'
   */
  const formatDateTime = (dateString) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return null;
      return date.toLocaleString('ru-RU');
    } catch (error) {
      return null;
    }
  };

  const exifFields = [
    { label: 'Камера', value: photo.camera },
    { label: 'Объектив', value: photo.lens_model },
    { label: 'Диафрагма', value: photo.aperture },
    { label: 'Выдержка', value: photo.exposure ? `${photo.exposure} с` : null },
    { label: 'ISO', value: photo.iso ? `ISO ${photo.iso}` : null },
    { label: 'Фокусное расстояние', value: photo.focal_length ? `${photo.focal_length} мм` : null },
    { label: 'Дата съёмки', value: formatDateTime(photo.datetime_taken) },
  ];

  const filledFields = exifFields.filter(field => field.value);

  if (filledFields.length === 0) {
    return null;
  }

  return (
    <Table striped bordered size="sm" className="mb-0">
      <tbody>
        {filledFields.map((field, index) => (
          <tr key={index}>
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

ExifData.propTypes = {
  photo: PropTypes.shape({
    camera: PropTypes.string,
    lens_model: PropTypes.string,
    aperture: PropTypes.string,
    exposure: PropTypes.string,
    iso: PropTypes.number,
    focal_length: PropTypes.number,
    datetime_taken: PropTypes.string,
  }).isRequired,
};

export default ExifData;
