import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AlbumSelector from './AlbumSelector';

/**
 * Тесты для компонента AlbumSelector.
 * Проверяют отображение списка альбомов, выбор альбома пользователем,
 * обработку состояний загрузки и пустого списка.
 */

describe('AlbumSelector', () => {
  // Мок-данные альбомов для тестирования
  const mockAlbums = [
    { id: 1, name: 'Альбом 1' },
    { id: 2, name: 'Альбом 2' },
    { id: 3, name: 'Альбом 3' },
  ];

  // Проверяет отображение заголовка селектора альбома
  test('рендерит с лейблом', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText('Выберите альбом')).toBeInTheDocument();
  });

  // Проверяет отображение опции по умолчанию в селекте
  test('рендерит опцию по умолчанию', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText('-- Выберите альбом --')).toBeInTheDocument();
  });

  // Проверяет отображение всех альбомов из переданного массива
  test('рендерит все альбомы', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText('Альбом 1')).toBeInTheDocument();
    expect(screen.getByText('Альбом 2')).toBeInTheDocument();
    expect(screen.getByText('Альбом 3')).toBeInTheDocument();
  });

  // Проверяет отображение выбранного альбома в селекте
  test('отображает выбранный альбом', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={2}
        onChange={jest.fn()}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('2');
  });

  // Проверяет вызов обработчика onChange с числовым ID при выборе альбома
  test('вызывает onChange с числовым ID при выборе альбома', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={handleChange}
      />
    );

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '2');

    expect(handleChange).toHaveBeenCalledWith(2);
  });

  // Проверяет вызов обработчика onChange с null при сбросе выбора
  test('вызывает onChange с null при выборе опции по умолчанию', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={1}
        onChange={handleChange}
      />
    );

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '');

    expect(handleChange).toHaveBeenCalledWith(null);
  });

  // Проверяет блокировку селекта при загрузке данных
  test('селект отключен если loading=true', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
        loading={true}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  // Проверяет блокировку селекта при отсутствии альбомов
  test('селект отключен если albums пустой', () => {
    render(
      <AlbumSelector
        albums={[]}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  // Проверяет активность селекта при наличии альбомов и завершении загрузки
  test('селект активен если не loading и есть albums', () => {
    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
        loading={false}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).not.toBeDisabled();
  });

  // Проверяет корректную обработку большого количества альбомов
  test('рендерит с большим количеством альбомов', () => {
    const manyAlbums = Array.from({ length: 50 }, (_, i) => ({
      id: i + 1,
      name: `Альбом ${i + 1}`,
    }));

    render(
      <AlbumSelector
        albums={manyAlbums}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    const select = screen.getByRole('combobox');
    const options = select.querySelectorAll('option');
    expect(options).toHaveLength(51); // +1 для опции по умолчанию
  });

  // Проверяет отображение длинных названий альбомов
  test('рендерит с длинными названиями альбомов', () => {
    const albumsWithLongNames = [
      { id: 1, name: 'Очень длинное название альбома которое может занимать много места' },
    ];

    render(
      <AlbumSelector
        albums={albumsWithLongNames}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText(albumsWithLongNames[0].name)).toBeInTheDocument();
  });

  // Проверяет корректную обработку спецсимволов в названиях альбомов
  test('рендерит со спецсимволами в названиях', () => {
    const albumsWithSpecialChars = [
      { id: 1, name: 'Альбом <>&"\'' },
    ];

    render(
      <AlbumSelector
        albums={albumsWithSpecialChars}
        selectedAlbum={null}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText(albumsWithSpecialChars[0].name)).toBeInTheDocument();
  });

  // Проверяет последовательный выбор различных альбомов
  test('выбор различных альбомов', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(
      <AlbumSelector
        albums={mockAlbums}
        selectedAlbum={null}
        onChange={handleChange}
      />
    );

    const select = screen.getByRole('combobox');

    await user.selectOptions(select, '1');
    expect(handleChange).toHaveBeenLastCalledWith(1);

    await user.selectOptions(select, '3');
    expect(handleChange).toHaveBeenLastCalledWith(3);
  });
});
