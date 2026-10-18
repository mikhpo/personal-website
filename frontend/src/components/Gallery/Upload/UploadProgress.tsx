import React from 'react';
import { ProgressBar } from 'react-bootstrap';

/** Статус загрузки файла. */
export type UploadStatus = 'uploading' | 'success' | 'error';

/** Свойства компонента индикатора загрузки файлов. */
export interface UploadProgressProps {
  /** Прогресс загрузки (0-100). */
  progress: number;
  /** Название файла. */
  fileName: string;
  /** Статус загрузки. */
  status: UploadStatus;
}

/**
 * Компонент индикатора загрузки файлов.
 *
 * Отображает прогресс бар для загружаемого файла с индикацией статуса.
 */
const UploadProgress = ({ progress, fileName, status }: UploadProgressProps) => {
  /** Цветовая схема progress bar в зависимости от статуса загрузки. */
  const getVariant = (): string => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'danger';
      case 'uploading':
      default:
        return 'primary';
    }
  };

  /** Текст статуса загрузки для отображения пользователю. */
  const getStatusText = (): string => {
    switch (status) {
      case 'success':
        return 'Загружено';
      case 'error':
        return 'Ошибка';
      case 'uploading':
      default:
        return `Загрузка... ${progress}%`;
    }
  };

  // Анимация progress bar активна только во время загрузки
  const isAnimated = status === 'uploading';

  return (
    <div className="mb-3">
      <div className="d-flex justify-content-between align-items-center mb-1">
        <small className="text-truncate" style={{ maxWidth: '70%' }}>
          {fileName}
        </small>
        <small className="text-muted">{getStatusText()}</small>
      </div>
      <ProgressBar now={progress} variant={getVariant()} animated={isAnimated} striped={isAnimated} />
    </div>
  );
};

export default UploadProgress;
