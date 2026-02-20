import React from 'react';
import { ProgressBar } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент индикатора загрузки файлов.
 *
 * Отображает прогресс бар для загружаемого файла с индикацией статуса.
 *
 * @param {Object} props - Пропсы компонента
 * @param {number} props.progress - Прогресс загрузки (0-100)
 * @param {string} props.fileName - Название файла
 * @param {string} props.status - Статус загрузки: 'uploading', 'success', 'error'
 * @return {JSX.Element} Компонент индикатора загрузки
 */
const UploadProgress = ({ progress, fileName, status }) => {
  /**
   * Определяет цветовую схему progress bar в зависимости от статуса загрузки.
   *
   * @function
   * @return {string} Вариант Bootstrap (primary, success, danger)
   */
  const getVariant = () => {
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

  /**
   * Возвращает текст статуса загрузки для отображения пользователю.
   *
   * @function
   * @return {string} Текстовое описание статуса
   */
  const getStatusText = () => {
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
      <ProgressBar
        now={progress}
        variant={getVariant()}
        animated={isAnimated}
        striped={isAnimated}
      />
    </div>
  );
};

UploadProgress.propTypes = {
  progress: PropTypes.number.isRequired,
  fileName: PropTypes.string.isRequired,
  status: PropTypes.oneOf(['uploading', 'success', 'error']).isRequired,
};

export default UploadProgress;
