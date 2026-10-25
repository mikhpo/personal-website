import { useCallback, useState } from 'react';
import { galleryService } from '@services';
import { getErrorMessage } from '@utils/errors';
import type { UploadStatus } from '@components/Gallery/Upload/UploadProgress';

/** Прогресс загрузки одного файла. */
export interface FileProgress {
  progress: number;
  status: UploadStatus;
}

/** Результат загрузки одного файла. */
export interface UploadOutcome {
  file: string;
  success: boolean;
  error?: string;
}

/** Результат хука usePhotoUpload. */
export interface UsePhotoUploadResult {
  /** Прогресс загрузки по имени файла. */
  uploadProgress: Record<string, FileProgress>;
  /** Идет ли загрузка. */
  uploading: boolean;
  /**
   * Последовательно загружает файлы в альбом, ведет прогресс по каждому файлу
   * и возвращает итоги загрузки.
   */
  upload: (albumId: number, files: File[]) => Promise<UploadOutcome[]>;
  /** Очищает прогресс загрузки. */
  resetProgress: () => void;
}

/**
 * Хук для последовательной загрузки фотографий с ведением прогресса.
 *
 * Загружает файлы по одному через сервис галереи, обновляет прогресс
 * по завершении каждого файла и собирает итоги для обработки вызывающим
 * компонентом.
 */
const usePhotoUpload = (): UsePhotoUploadResult => {
  /** Прогресс загрузки по имени файла. */
  const [uploadProgress, setUploadProgress] = useState<Record<string, FileProgress>>({});

  /** Идет ли загрузка. */
  const [uploading, setUploading] = useState(false);

  const upload = useCallback(async (albumId: number, files: File[]): Promise<UploadOutcome[]> => {
    setUploading(true);
    setUploadProgress({});

    const outcomes: UploadOutcome[] = [];

    for (const file of files) {
      try {
        await galleryService.uploadPhoto(albumId, file);
        outcomes.push({ file: file.name, success: true });
        setUploadProgress((prev) => ({ ...prev, [file.name]: { progress: 100, status: 'success' } }));
      } catch (err) {
        const message = getErrorMessage(err);
        outcomes.push({ file: file.name, success: false, error: message });
        setUploadProgress((prev) => ({ ...prev, [file.name]: { progress: 0, status: 'error' } }));
      }
    }

    setUploading(false);
    return outcomes;
  }, []);

  const resetProgress = useCallback(() => {
    setUploadProgress({});
  }, []);

  return { uploadProgress, uploading, upload, resetProgress };
};

export default usePhotoUpload;
