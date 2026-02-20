import React from 'react';
import { render, screen } from '@testing-library/react';
import UploadProgress from './UploadProgress';

/**
 * Тесты для компонента UploadProgress.
 * Проверяют отображение прогресса загрузки, статусов (uploading, success, error),
 * анимации и корректность отображения информации о файле.
 */

describe('UploadProgress', () => {
  // Проверяет базовый рендеринг компонента с основными пропсами
  test('рендерит с базовыми props', () => {
    render(
      <UploadProgress
        progress={50}
        fileName="test.jpg"
        status="uploading"
      />
    );

    expect(screen.getByText('test.jpg')).toBeInTheDocument();
    expect(screen.getByText('Загрузка... 50%')).toBeInTheDocument();
  });

  // Проверяет отображение статуса загрузки
  test('отображает статус "uploading"', () => {
    render(
      <UploadProgress
        progress={30}
        fileName="file.jpg"
        status="uploading"
      />
    );

    expect(screen.getByText('Загрузка... 30%')).toBeInTheDocument();
  });

  // Проверяет отображение статуса успешной загрузки
  test('отображает статус "success"', () => {
    render(
      <UploadProgress
        progress={100}
        fileName="file.jpg"
        status="success"
      />
    );

    expect(screen.getByText('Загружено')).toBeInTheDocument();
  });

  // Проверяет отображение статуса ошибки загрузки
  test('отображает статус "error"', () => {
    render(
      <UploadProgress
        progress={50}
        fileName="file.jpg"
        status="error"
      />
    );

    expect(screen.getByText('Ошибка')).toBeInTheDocument();
  });

  // Проверяет корректность значения прогресса в progress bar
  test('progress bar имеет правильное значение', () => {
    const { container } = render(
      <UploadProgress
        progress={75}
        fileName="file.jpg"
        status="uploading"
      />
    );

    const progressBar = container.querySelector('.progress-bar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '75');
  });

  // Проверяет отображение начального состояния прогресса
  test('рендерит с прогрессом 0%', () => {
    render(
      <UploadProgress
        progress={0}
        fileName="file.jpg"
        status="uploading"
      />
    );

    expect(screen.getByText('Загрузка... 0%')).toBeInTheDocument();
  });

  // Проверяет отображение завершенного прогресса
  test('рендерит с прогрессом 100%', () => {
    render(
      <UploadProgress
        progress={100}
        fileName="file.jpg"
        status="uploading"
      />
    );

    expect(screen.getByText('Загрузка... 100%')).toBeInTheDocument();
  });

  // Проверяет корректное отображение различных названий файлов
  test('рендерит с различными названиями файлов', () => {
    const fileNames = ['image.jpg', 'photo.png', 'picture.gif'];

    fileNames.forEach(fileName => {
      const { unmount } = render(
        <UploadProgress
          progress={50}
          fileName={fileName}
          status="uploading"
        />
      );
      expect(screen.getByText(fileName)).toBeInTheDocument();
      unmount();
    });
  });

  // Проверяет корректную обработку спецсимволов в названии файла
  test('рендерит со спецсимволами в названии файла', () => {
    render(
      <UploadProgress
        progress={50}
        fileName='file <>&".jpg'
        status="uploading"
      />
    );

    expect(screen.getByText('file <>&".jpg', { exact: false })).toBeInTheDocument();
  });

  // Проверяет отображение очень длинных названий файлов
  test('рендерит с очень длинным названием файла', () => {
    const longFileName = 'a'.repeat(200) + '.jpg';
    render(
      <UploadProgress
        progress={50}
        fileName={longFileName}
        status="uploading"
      />
    );

    expect(screen.getByText(longFileName)).toBeInTheDocument();
  });
});
