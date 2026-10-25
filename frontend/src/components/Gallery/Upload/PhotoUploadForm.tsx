import React, { useCallback, useState } from 'react';
import { Card, Button, Alert } from 'react-bootstrap';
import AlbumSelector from '@components/Gallery/Upload/AlbumSelector';
import FileDropzone from '@components/Gallery/Upload/FileDropzone';
import UploadProgress from '@components/Gallery/Upload/UploadProgress';
import Spinner from '@components/Spinner/Spinner';
import LoadingError from '@components/Alert/LoadingError';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { useApiData, usePhotoUpload } from '@hooks';

/**
 * Компонент формы загрузки фотографий.
 *
 * Позволяет выбрать альбом и загрузить фотографии через drag-and-drop
 * или file input.
 */
const PhotoUploadForm = () => {
  const [selectedAlbum, setSelectedAlbum] = useState<number | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  const loadAlbums = useCallback(async () => {
    const data = await galleryService.getAlbums();
    return parseListResponse(data).items;
  }, []);

  const {
    data: albumsData,
    loading: loadingAlbums,
    error: albumsError,
    refetch: refetchAlbums,
  } = useApiData(loadAlbums);
  const albums = albumsData ?? [];

  /** Прогресс и оркестрация загрузки файлов. */
  const { uploadProgress, uploading, upload, resetProgress } = usePhotoUpload();

  /**
   * Повторно запрашивает список альбомов с сервера по кнопке "Повторить".
   */
  const handleRetryAlbums = () => {
    refetchAlbums();
  };

  /**
   * Устанавливает выбранные файлы в состояние и очищает сообщения
   * об ошибках и успехе.
   */
  const handleFilesSelect = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setErrors([]);
    setSuccess(false);
  };

  /**
   * Валидирует выбранные файлы и альбом, затем последовательно загружает
   * каждый файл на сервер с отображением прогресса и обновляет состояние
   * формы по результатам.
   */
  const handleUpload = async () => {
    setErrors([]);
    setSuccess(false);

    if (!selectedAlbum) {
      setErrors(['Пожалуйста, выберите альбом']);
      return;
    }

    if (files.length === 0) {
      setErrors(['Пожалуйста, выберите файлы для загрузки']);
      return;
    }

    const uploadResults = await upload(selectedAlbum, files);

    const failedUploads = uploadResults.filter((r) => !r.success);
    if (failedUploads.length > 0) {
      setErrors(failedUploads.map((r) => `${r.file}: ${r.error}`));
    }

    const successfulUploads = uploadResults.filter((r) => r.success);
    if (successfulUploads.length > 0) {
      setSuccess(true);
      if (failedUploads.length === 0) {
        // Сбросить форму только если все файлы загружены успешно
        setFiles([]);
        resetProgress();
      }
    }
  };

  if (loadingAlbums) {
    return <Spinner message="Загрузка альбомов..." />;
  }

  if (albumsError) {
    return <LoadingError message={albumsError} onRetry={handleRetryAlbums} />;
  }

  return (
    <Card className="shadow-sm p-3 mb-5 rounded">
      <Card.Body>
        <Card.Title as="h1" className="fs-4">
          Загрузка фотографий
        </Card.Title>

        <AlbumSelector
          albums={albums}
          selectedAlbum={selectedAlbum}
          onChange={setSelectedAlbum}
          loading={loadingAlbums}
        />

        <FileDropzone onFilesSelect={handleFilesSelect} accept="image/*" multiple={true} files={files} />

        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4">
            <h2 className="fs-6">Прогресс загрузки:</h2>
            {Object.entries(uploadProgress).map(([fileName, progress]) => (
              <UploadProgress
                key={fileName}
                fileName={fileName}
                progress={progress.progress}
                status={progress.status}
              />
            ))}
          </div>
        )}

        {errors.length > 0 && (
          <Alert variant="danger" className="mt-3">
            <Alert.Heading as="h2" className="fs-4">
              Ошибки загрузки
            </Alert.Heading>
            <ul className="mb-0">
              {errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          </Alert>
        )}

        {success && (
          <Alert variant="success" className="mt-3">
            Фотографии успешно загружены!
          </Alert>
        )}

        <div className="d-flex justify-content-end mt-3">
          <Button variant="primary" onClick={handleUpload} disabled={uploading || !selectedAlbum || files.length === 0}>
            {uploading ? 'Загрузка...' : 'Загрузить'}
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

export default PhotoUploadForm;
