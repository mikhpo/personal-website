import React from 'react';
import { Form } from 'react-bootstrap';
import type { components } from '@api-types/api-schema';

type AlbumList = components['schemas']['AlbumList'];

/** Свойства компонента выбора альбома. */
export interface AlbumSelectorProps {
  /** Массив альбомов; компонент читает только id и наименование. */
  albums: Pick<AlbumList, 'id' | 'name'>[];
  /** ID выбранного альбома. */
  selectedAlbum: number | null;
  /** Обработчик изменения выбора. */
  onChange: (albumId: number | null) => void;
  /** Флаг загрузки. */
  loading?: boolean;
}

/**
 * Компонент выбора альбома.
 *
 * Отображает выпадающий список для выбора альбома из загруженного списка.
 */
const AlbumSelector = ({ albums, selectedAlbum, onChange, loading = false }: AlbumSelectorProps) => {
  /**
   * Преобразует строковое значение из select в числовой ID альбома
   * или null при выборе опции по умолчанию.
   */
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onChange(value ? parseInt(value, 10) : null);
  };

  return (
    <Form.Group className="mb-3">
      <Form.Label>Выберите альбом</Form.Label>
      <Form.Select value={selectedAlbum || ''} onChange={handleChange} disabled={loading || albums.length === 0}>
        <option value="">-- Выберите альбом --</option>
        {albums.map((album) => (
          <option key={album.id} value={album.id}>
            {album.name}
          </option>
        ))}
      </Form.Select>
    </Form.Group>
  );
};

export default AlbumSelector;
