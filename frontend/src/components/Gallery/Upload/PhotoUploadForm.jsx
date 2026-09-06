import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'react-bootstrap';
import AlbumSelector from '@components/Gallery/Upload/AlbumSelector';
import FileDropzone from '@components/Gallery/Upload/FileDropzone';
import UploadProgress from '@components/Gallery/Upload/UploadProgress';
import SpinnerComponent from '@components/Spinner/Spinner';
import { galleryService } from '@services';

/**
 * Компонент формы загрузки фотографий.
 *
 * Позволяет выбрать альбом и загрузить фотографии через drag-and-drop или file input.
 *
 * @param {Object} props - Пропсы компонента
 * @return {JSX.Element} Компонент формы загрузки
 */
const PhotoUploadForm = () => {
  const [albums, setAlbums] = useState([]);
  const [selectedAlbum, setSelectedAlbum] = useState(null);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [errors, setErrors] = useState([]);
  const [success, setSuccess] = useState(false);
  const [loadingAlbums, setLoadingAlbums] = useState(true);
  const [albumsError, setAlbumsError] = useState(null);

  useEffect(() => {
    const fetchAlbums = () => {
      const updateLoadingState = () => {
        setLoadingAlbums(true);
        setAlbumsError(null);
      };
      updateLoadingState();

      galleryService.getAlbums()
        .then(data => {
          const albumsList = data.results || data;
          setAlbums(Array.isArray(albumsList) ? albumsList : []);
          setLoadingAlbums(false);
        })
        .catch(err => {
          setAlbumsError(err.message);
          setLoadingAlbums(false);
        });
    };

    fetchAlbums();
  }, []);

  /**
   * Обработчик выбора файлов пользователем.
   *
   * Устанавливает выбранные файлы в состояние и очищает сообщения об ошибках и успехе.
   *
   * @function
   * @param {File[]} selectedFiles - Массив выбранных файлов
   * @return {void}
   */
  const handleFilesSelect = (selectedFiles) => {
    setFiles(selectedFiles);
    setErrors([]);
    setSuccess(false);
  };

  /**
   * Обработчик загрузки фотографий на сервер.
   *
   * Выполняет валидацию выбранных файлов и альбома, затем последовательно загружает
   * каждый файл на сервер с отображением прогресса. После завершения загрузки
   * обновляет состояние формы и отображает результаты.
   *
   * @async
   * @function
   * @return {Promise<void>} Промис, который разрешается после завершения загрузки всех файлов
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

    setUploading(true);

    // Колбэк для обновления прогресса загрузки
    const onProgress = (fileName, progressData) => {
      setUploadProgress(prev => ({
        ...prev,
        [fileName]: progressData,
      }));
    };

    const uploadResults = await galleryService.uploadPhotos(
      selectedAlbum,
      files,
      onProgress
    );

    setUploading(false);

    const failedUploads = uploadResults.filter(r => !r.success);
    if (failedUploads.length > 0) {
      setErrors(failedUploads.map(r => `${r.file}: ${r.error}`));
    }

    const successfulUploads = uploadResults.filter(r => r.success);
    if (successfulUploads.length > 0) {
      setSuccess(true);
      if (failedUploads.length === 0) {
        // Сбросить форму только если все файлы загружены успешно
        setFiles([]);
        setUploadProgress({});
      }
    }
  };

  /**
   * Обработчик повторной попытки загрузки альбомов после ошибки.
   *
   * Сбрасывает состояние ошибки и повторно запрашивает список альбомов с сервера.
   * Используется при нажатии пользователем кнопки "Повторить" в сообщении об ошибке.
   *
   * @function
   * @return {void}
   */
  const handleRetryAlbums = () => {
    setLoadingAlbums(true);
    setAlbumsError(null);

    galleryService.getAlbums()
      .then(data => {
        const albumsList = data.results || data;
        setAlbums(Array.isArray(albumsList) ? albumsList : []);
        setLoadingAlbums(false);
      })
      .catch(err => {
        setAlbumsError(err.message);
        setLoadingAlbums(false);
      });
  };

  if (loadingAlbums) {
    return <SpinnerComponent message="Загрузка альбомов..." />;
  }

  if (albumsError) {
    return (
      <div className="container mt-3">
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <div>
            {albumsError}
            <button className="btn btn-sm btn-primary ms-2" onClick={handleRetryAlbums}>
              Повторить
            </button>
          </div>
          <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      </div>
    );
  }

  return (
    <Card className="shadow-sm p-3 mb-5 bg-white rounded">
      <Card.Body>
        <Card.Title as="h1" className="fs-4">Загрузка фотографий</Card.Title>

        <AlbumSelector
          albums={albums}
          selectedAlbum={selectedAlbum}
          onChange={setSelectedAlbum}
          loading={loadingAlbums}
        />

        <FileDropzone
          onFilesSelect={handleFilesSelect}
          accept="image/*"
          multiple={true}
          files={files}
        />

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
            <Alert.Heading as="h2" className="fs-4">Ошибки загрузки</Alert.Heading>
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
          <Button
            variant="primary"
            onClick={handleUpload}
            disabled={uploading || !selectedAlbum || files.length === 0}
          >
            {uploading ? 'Загрузка...' : 'Загрузить'}
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

PhotoUploadForm.propTypes = {};

export default PhotoUploadForm;
