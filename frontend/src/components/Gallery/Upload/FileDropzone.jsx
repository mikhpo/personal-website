import React, { useState, useRef, useEffect } from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент drag-and-drop зоны для файлов.
 *
 * Позволяет выбрать файлы через клик или перетаскивание.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Function} props.onFilesSelect - Обработчик выбора файлов
 * @param {string} [props.accept="image/*"] - Типы принимаемых файлов
 * @param {boolean} [props.multiple=true] - Разрешить выбор нескольких файлов
 * @param {Array} [props.files=[]] - Управляемые файлы извне (для сброса)
 * @return {JSX.Element} Компонент drag-and-drop зоны
 */
const FileDropzone = ({ onFilesSelect, accept = 'image/*', multiple = true, files = null }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const inputRef = useRef(null);

  // Синхронизация локального состояния с управляемыми файлами извне
  useEffect(() => {
    const initializeFiles = () => {
      if (files !== null && Array.isArray(files)) {
        const updateFilesState = () => {
          setSelectedFiles(files);
        };
        updateFilesState();
      }
    };
    initializeFiles();
  }, [files]);

  /**
   * Обработчик событий перетаскивания файлов.
   *
   * Устанавливает активное состояние зоны при наведении файлов и деактивирует при уходе курсора.
   *
   * @function
   * @param {DragEvent} e - Событие перетаскивания
   * @return {void}
   */
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  /**
   * Валидирует файлы по типу или расширению.
   *
   * Фильтрует массив файлов согласно атрибуту accept компонента.
   * Поддерживает MIME-типы (image/*, image/jpeg) и расширения (.jpg, .png).
   *
   * @function
   * @param {FileList} files - Список файлов для валидации
   * @return {File[]} Отфильтрованный массив валидных файлов
   */
  const validateFiles = (files) => {
    if (!accept) return files;

    const acceptedTypes = accept.split(',').map(type => type.trim());
    return Array.from(files).filter(file => {
      if (acceptedTypes.includes('image/*')) {
        return file.type.startsWith('image/');
      }
      return acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return file.name.toLowerCase().endsWith(type.toLowerCase());
        }
        return file.type === type;
      });
    });
  };

  /**
   * Обработчик сброса файлов в зону drag-and-drop.
   *
   * Валидирует файлы, применяет ограничение по количеству (если multiple=false),
   * обновляет состояние и вызывает обработчик onFilesSelect.
   *
   * @function
   * @param {DragEvent} e - Событие сброса файлов
   * @return {void}
   */
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const validFiles = validateFiles(e.dataTransfer.files);
      const filesToUse = multiple ? validFiles : validFiles.slice(0, 1);

      if (files === null) {
        setSelectedFiles(filesToUse);
      }
      onFilesSelect(filesToUse);
    }
  };

  /**
   * Обработчик выбора файлов через стандартный диалог.
   *
   * Валидирует выбранные файлы, применяет ограничение по количеству,
   * обновляет состояние и вызывает обработчик onFilesSelect.
   *
   * @function
   * @param {Event} e - Событие изменения input[type="file"]
   * @return {void}
   */
  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const validFiles = validateFiles(e.target.files);
      const filesToUse = multiple ? validFiles : validFiles.slice(0, 1);

      if (files === null) {
        setSelectedFiles(filesToUse);
      }
      onFilesSelect(filesToUse);
    }
  };

  /**
   * Обработчик клика на зону dropzone.
   *
   * Открывает стандартный диалог выбора файлов.
   *
   * @function
   * @return {void}
   */
  const handleClick = () => {
    inputRef.current?.click();
  };

  /**
   * Удаляет файл из списка выбранных по индексу.
   *
   * Обновляет состояние и вызывает обработчик onFilesSelect с обновленным списком.
   *
   * @function
   * @param {number} index - Индекс файла для удаления
   * @return {void}
   */
  const removeFile = (index) => {
    const currentFiles = files !== null ? files : selectedFiles;
    const newFiles = currentFiles.filter((_, i) => i !== index);

    if (files === null) {
      setSelectedFiles(newFiles);
    }
    onFilesSelect(newFiles);
  };

  // Использовать управляемые файлы если переданы, иначе локальное состояние
  const displayFiles = files !== null ? files : selectedFiles;

  return (
    <div>
      <Card
        className={`p-5 text-center ${dragActive ? 'border-primary bg-light' : 'border-secondary'}`}
        style={{ cursor: 'pointer', borderStyle: 'dashed', borderWidth: '2px' }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <Card.Body>
          <p className="mb-2">
            {dragActive
              ? 'Отпустите файлы здесь'
              : 'Перетащите файлы сюда или кликните для выбора'}
          </p>
          <small className="text-muted">
            {multiple ? 'Можно выбрать несколько файлов' : 'Можно выбрать один файл'}
          </small>
        </Card.Body>
      </Card>
      <input
        ref={inputRef}
        type="file"
        multiple={multiple}
        accept={accept}
        onChange={handleChange}
        style={{ display: 'none' }}
      />
      {displayFiles.length > 0 && (
        <div className="mt-3">
          <h6>Выбранные файлы:</h6>
          <ul className="list-group">
            {displayFiles.map((file) => (
              <li
                key={`${file.name}-${file.size}-${file.lastModified}`}
                className="list-group-item d-flex justify-content-between align-items-center"
              >
                <span>{file.name}</span>
                <button
                  type="button"
                  className="btn btn-sm btn-danger"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(displayFiles.indexOf(file));
                  }}
                >
                  Удалить
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

FileDropzone.propTypes = {
  onFilesSelect: PropTypes.func.isRequired,
  accept: PropTypes.string,
  multiple: PropTypes.bool,
  files: PropTypes.array,
};

export default FileDropzone;
