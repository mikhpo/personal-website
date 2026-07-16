import React from 'react';
import { Form } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент выбора альбома.
 *
 * Отображает выпадающий список для выбора альбома из загруженного списка.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Array<Object>} props.albums - Массив объектов альбомов
 * @param {number} props.albums[].id - ID альбома
 * @param {string} props.albums[].name - Название альбома
 * @param {number|null} props.selectedAlbum - ID выбранного альбома
 * @param {Function} props.onChange - Обработчик изменения выбора
 * @param {boolean} [props.loading=false] - Флаг загрузки
 * @return {JSX.Element} Компонент селектора альбома
 */
const AlbumSelector = ({ albums, selectedAlbum, onChange, loading = false }) => {
  /**
   * Обработчик изменения выбора альбома.
   *
   * Преобразует строковое значение из select в числовой ID альбома
   * или null при выборе опции по умолчанию.
   *
   * @function
   * @param {Event} e - Событие изменения select
   * @return {void}
   */
  const handleChange = (e) => {
    const value = e.target.value;
    onChange(value ? parseInt(value, 10) : null);
  };

  return (
    <Form.Group className="mb-3">
      <Form.Label>Выберите альбом</Form.Label>
      <Form.Select
        value={selectedAlbum || ''}
        onChange={handleChange}
        disabled={loading || albums.length === 0}
      >
        <option value="">-- Выберите альбом --</option>
        {albums.map(album => (
          <option key={album.id} value={album.id}>
            {album.name}
          </option>
        ))}
      </Form.Select>
    </Form.Group>
  );
};

AlbumSelector.propTypes = {
  albums: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
    })
  ).isRequired,
  selectedAlbum: PropTypes.number,
  onChange: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

export default AlbumSelector;
