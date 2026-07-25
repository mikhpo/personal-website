import React from 'react';
import { Button } from 'react-bootstrap';
import AlertList from '@components/Alert/AlertList';

/**
 * Компонент для отображения ошибки загрузки с кнопкой повтора.
 *
 * Объединяет паттерн отображения ошибки с возможностью перезапроса данных,
 * который используется в AlbumList, SeriesGrid и CategoryGrid.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} props.message - Сообщение об ошибке для отображения
 * @param {Function} props.onRetry - Функция для повторной загрузки данных
 * @param {string} [props.retryButtonText='Повторить'] - Текст на кнопке повтора
 * @return {JSX.Element|null} Компонент AlertList или null, если сообщение пустое
 *
 * @example
 * <LoadingError
 *   message="Ошибка загрузки альбомов"
 *   onRetry={() => fetchAlbums()}
 * />
 */
const LoadingError = ({ message, onRetry, retryButtonText = 'Повторить' }) => {
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
            <Button
              variant="outline-primary"
              size="sm"
              onClick={onRetry}
              data-testid="retry-button"
            >
              {retryButtonText}
            </Button>
          ),
        },
      ]}
    />
  );
};

export default LoadingError;
