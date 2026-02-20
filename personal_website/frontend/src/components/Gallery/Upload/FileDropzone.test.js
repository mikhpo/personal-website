import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FileDropzone from './FileDropzone';

/**
 * Тесты для компонента FileDropzone.
 * Проверяют drag-and-drop функциональность, выбор файлов через input,
 * валидацию типов файлов и управление списком выбранных файлов.
 */

describe('FileDropzone', () => {
  // Вспомогательная функция для создания mock файла
  const createMockFile = (name, type) => {
    return new File(['content'], name, { type });
  };

  // Проверяет отображение текста по умолчанию
  test('рендерит текст по умолчанию', () => {
    render(<FileDropzone onFilesSelect={jest.fn()} />);

    expect(screen.getByText(/Перетащите файлы сюда или кликните для выбора/)).toBeInTheDocument();
  });

  // Проверяет отображение подсказки для множественного выбора
  test('показывает текст для множественного выбора', () => {
    render(<FileDropzone onFilesSelect={jest.fn()} multiple={true} />);

    expect(screen.getByText('Можно выбрать несколько файлов')).toBeInTheDocument();
  });

  // Проверяет отображение подсказки для одиночного выбора
  test('показывает текст для одиночного выбора', () => {
    render(<FileDropzone onFilesSelect={jest.fn()} multiple={false} />);

    expect(screen.getByText('Можно выбрать один файл')).toBeInTheDocument();
  });

  // Проверяет визуальную активацию зоны при перетаскивании файлов
  test('активируется при dragenter', () => {
    const { container } = render(<FileDropzone onFilesSelect={jest.fn()} />);

    const dropzone = container.querySelector('.card');
    fireEvent.dragEnter(dropzone);

    expect(screen.getByText('Отпустите файлы здесь')).toBeInTheDocument();
  });

  // Проверяет деактивацию зоны при уходе курсора
  test('деактивируется при dragleave', () => {
    const { container } = render(<FileDropzone onFilesSelect={jest.fn()} />);

    const dropzone = container.querySelector('.card');
    fireEvent.dragEnter(dropzone);
    fireEvent.dragLeave(dropzone);

    expect(screen.getByText(/Перетащите файлы сюда/)).toBeInTheDocument();
  });

  // Проверяет обработку сброса файлов в зону drag-and-drop
  test('обрабатывает drop файлов', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(<FileDropzone onFilesSelect={handleFilesSelect} />);

    const dropzone = container.querySelector('.card');
    const files = [createMockFile('test.jpg', 'image/jpeg')];

    fireEvent.drop(dropzone, {
      dataTransfer: { files },
    });

    expect(handleFilesSelect).toHaveBeenCalledWith(files);
  });

  // Проверяет открытие диалога выбора файлов при клике на зону
  test('вызывает клик на input при клике на dropzone', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileDropzone onFilesSelect={jest.fn()} />);

    const dropzone = container.querySelector('.card');
    const input = container.querySelector('input[type="file"]');

    const clickSpy = jest.spyOn(input, 'click');

    await user.click(dropzone);

    expect(clickSpy).toHaveBeenCalled();
  });

  // Проверяет выбор файлов через стандартный диалог
  test('обрабатывает выбор файлов через input', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(<FileDropzone onFilesSelect={handleFilesSelect} />);

    const input = container.querySelector('input[type="file"]');
    const files = [createMockFile('test.jpg', 'image/jpeg')];

    fireEvent.change(input, { target: { files } });

    expect(handleFilesSelect).toHaveBeenCalledWith(files);
  });

  // Проверяет фильтрацию файлов по типу image/*
  test('фильтрует файлы по типу image/*', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(
      <FileDropzone onFilesSelect={handleFilesSelect} accept="image/*" />
    );

    const dropzone = container.querySelector('.card');
    const files = [
      createMockFile('test.jpg', 'image/jpeg'),
      createMockFile('test.txt', 'text/plain'),
    ];

    fireEvent.drop(dropzone, {
      dataTransfer: { files },
    });

    expect(handleFilesSelect).toHaveBeenCalledWith([files[0]]);
  });

  // Проверяет ограничение выбора одним файлом
  test('ограничивает выбор одним файлом если multiple=false', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(
      <FileDropzone onFilesSelect={handleFilesSelect} multiple={false} />
    );

    const dropzone = container.querySelector('.card');
    const files = [
      createMockFile('test1.jpg', 'image/jpeg'),
      createMockFile('test2.jpg', 'image/jpeg'),
    ];

    fireEvent.drop(dropzone, {
      dataTransfer: { files },
    });

    expect(handleFilesSelect).toHaveBeenCalledWith([files[0]]);
  });

  // Проверяет отображение списка выбранных файлов
  test('отображает список выбранных файлов', () => {
    const { container } = render(<FileDropzone onFilesSelect={jest.fn()} />);

    const input = container.querySelector('input[type="file"]');
    const files = [
      createMockFile('test1.jpg', 'image/jpeg'),
      createMockFile('test2.jpg', 'image/jpeg'),
    ];

    fireEvent.change(input, { target: { files } });

    expect(screen.getByText('Выбранные файлы:')).toBeInTheDocument();
    expect(screen.getByText('test1.jpg')).toBeInTheDocument();
    expect(screen.getByText('test2.jpg')).toBeInTheDocument();
  });

  // Проверяет удаление файла из списка выбранных
  test('удаляет файл из списка', async () => {
    const user = userEvent.setup();
    const handleFilesSelect = jest.fn();
    const { container } = render(<FileDropzone onFilesSelect={handleFilesSelect} />);

    const input = container.querySelector('input[type="file"]');
    const files = [
      createMockFile('test1.jpg', 'image/jpeg'),
      createMockFile('test2.jpg', 'image/jpeg'),
    ];

    fireEvent.change(input, { target: { files } });

    const deleteButtons = screen.getAllByText('Удалить');
    await user.click(deleteButtons[0]);

    expect(handleFilesSelect).toHaveBeenLastCalledWith([files[1]]);
  });

  // Проверяет скрытие списка при отсутствии выбранных файлов
  // Проверяет скрытие списка при отсутствии выбранных файлов
  test('не отображает список если файлы не выбраны', () => {
    render(<FileDropzone onFilesSelect={jest.fn()} />);

    expect(screen.queryByText('Выбранные файлы:')).not.toBeInTheDocument();
  });

  // Проверяет игнорирование пустого массива файлов
  test('обрабатывает пустой массив файлов при drop', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(<FileDropzone onFilesSelect={handleFilesSelect} />);

    const dropzone = container.querySelector('.card');

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [] },
    });

    expect(handleFilesSelect).not.toHaveBeenCalled();
  });

  // Проверяет фильтрацию файлов без типа при валидации
  test('обрабатывает файлы без типа', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(
      <FileDropzone onFilesSelect={handleFilesSelect} accept="image/*" />
    );

    const dropzone = container.querySelector('.card');
    const fileWithoutType = new File(['content'], 'test.jpg', { type: '' });

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [fileWithoutType] },
    });

    expect(handleFilesSelect).toHaveBeenCalledWith([]);
  });

  // Проверяет валидацию файлов по расширению
  test('валидация работает с расширениями файлов', () => {
    const handleFilesSelect = jest.fn();
    const { container } = render(
      <FileDropzone onFilesSelect={handleFilesSelect} accept=".jpg,.png" />
    );

    const dropzone = container.querySelector('.card');
    const files = [
      createMockFile('test.jpg', 'image/jpeg'),
      createMockFile('test.gif', 'image/gif'),
    ];

    fireEvent.drop(dropzone, {
      dataTransfer: { files },
    });

    expect(handleFilesSelect).toHaveBeenCalledWith([files[0]]);
  });

  // Проверяет скрытие списка при удалении всех файлов
  test('удаление всех файлов очищает список', async () => {
    const user = userEvent.setup();
    const handleFilesSelect = jest.fn();
    const { container } = render(<FileDropzone onFilesSelect={handleFilesSelect} />);

    const input = container.querySelector('input[type="file"]');
    const files = [createMockFile('test.jpg', 'image/jpeg')];

    fireEvent.change(input, { target: { files } });

    const deleteButton = screen.getByText('Удалить');
    await user.click(deleteButton);

    expect(screen.queryByText('Выбранные файлы:')).not.toBeInTheDocument();
  });
});
