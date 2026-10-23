import React from 'react';
import { Button } from 'react-bootstrap';
import AlertList from '@components/Alert/AlertList';

/** Свойства компонента ошибки загрузки. */
export interface LoadingErrorProps {
  /** Сообщение об ошибке для отображения. */
  message: string;
  /** Функция для повторной загрузки данных. */
  onRetry: () => void;
  /** Текст на кнопке повтора. */
  retryButtonText?: string;
}

/**
 * Компонент для отображения ошибки загрузки с кнопкой повтора.
 *
 * Объединяет паттерн отображения ошибки с возможностью перезапроса данных,
 * который используется в AlbumList, SeriesGrid и CategoryGrid.
 *
 * @example
 * <LoadingError
 *   message="Ошибка загрузки альбомов"
 *   onRetry={() => fetchAlbums()}
 * />
 */
const LoadingError = ({ message, onRetry, retryButtonText = 'Повторить' }: LoadingErrorProps) => {
  if (!message) {
    return null;
  }

  return (
    <AlertList
      messages={[
        {
          message,
          level: 'error',
          actions: (
            <Button variant="outline-primary" size="sm" onClick={onRetry} data-testid="retry-button">
              {retryButtonText}
            </Button>
          ),
        },
      ]}
    />
  );
};

export default LoadingError;
