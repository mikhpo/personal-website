/* eslint-disable react-x/set-state-in-effect -- синхронизация локального состояния с управляемыми файлами в effect - установленный дизайн компонента; перестройка меняла бы рантайм */
import React, { useEffect, useRef, useState } from 'react';
import { Card } from 'react-bootstrap';

/** Свойства компонента drag-and-drop зоны для файлов. */
export interface FileDropzoneProps {
  /** Обработчик выбора файлов. */
  onFilesSelect: (files: File[]) => void;
  /** Типы принимаемых файлов. */
  accept?: string;
  /** Разрешить выбор нескольких файлов. */
  multiple?: boolean;
  /** Управляемые файлы извне (для сброса). */
  files?: File[] | null;
}

/**
 * Компонент drag-and-drop зоны для файлов.
 *
 * Позволяет выбрать файлы через клик или перетаскивание.
 */
const FileDropzone = ({ onFilesSelect, accept = 'image/*', multiple = true, files = null }: FileDropzoneProps) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Синхронизация локального состояния с управляемыми файлами извне
  useEffect(() => {
    if (files !== null && Array.isArray(files)) {
      setSelectedFiles(files);
    }
  }, [files]);

  /**
   * Устанавливает активное состояние зоны при наведении файлов
   * и деактивирует при уходе курсора.
   */
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  /**
   * Валидирует файлы по типу или расширению согласно атрибуту accept:
   * поддерживает MIME-типы (image/*, image/jpeg) и расширения (.jpg, .png).
   */
  const validateFiles = (fileList: FileList): File[] => {
    if (!accept) return Array.from(fileList);

    const acceptedTypes = accept.split(',').map((type) => type.trim());
    return Array.from(fileList).filter((file) => {
      if (acceptedTypes.includes('image/*')) {
        return file.type.startsWith('image/');
      }
      return acceptedTypes.some((type) => {
        if (type.startsWith('.')) {
          return file.name.toLowerCase().endsWith(type.toLowerCase());
        }
        return file.type === type;
      });
    });
  };

  /**
   * Валидирует сброшенные файлы, применяет ограничение по количеству
   * (если multiple=false), обновляет состояние и вызывает onFilesSelect.
   */
  const handleDrop = (e: React.DragEvent) => {
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
   * Валидирует файлы из стандартного диалога, применяет ограничение
   * по количеству, обновляет состояние и вызывает onFilesSelect.
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const validFiles = validateFiles(e.target.files);
      const filesToUse = multiple ? validFiles : validFiles.slice(0, 1);

      if (files === null) {
        setSelectedFiles(filesToUse);
      }
      onFilesSelect(filesToUse);
    }
  };

  /** Открывает стандартный диалог выбора файлов. */
  const handleClick = () => {
    inputRef.current?.click();
  };

  /** Активирует выбор файлов клавишами Enter и Space. */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      inputRef.current?.click();
    }
  };

  /** Удаляет файл из списка выбранных по индексу. */
  const removeFile = (index: number) => {
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
        className={`p-5 text-center ${dragActive ? 'border-primary bg-body-tertiary' : 'border-secondary'}`}
        style={{ cursor: 'pointer', borderStyle: 'dashed', borderWidth: '2px' }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-label="Выбрать файлы для загрузки"
      >
        <Card.Body>
          <p className="mb-2">
            {dragActive ? 'Отпустите файлы здесь' : 'Перетащите файлы сюда или кликните для выбора'}
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
          <h2 className="fs-6">Выбранные файлы:</h2>
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

export default FileDropzone;
