import React, { useCallback } from 'react';
import { Offcanvas } from 'react-bootstrap';
import TagButton from '@components/Gallery/Tags/TagButton';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { useApiData } from '@hooks';

/** Свойства компонента боковой панели с тегами. */
export interface TagsOffcanvasProps {
  /** Показывать ли панель. */
  show: boolean;
  /** Обработчик закрытия панели. */
  onHide: () => void;
}

/**
 * Компонент боковой панели с тегами.
 *
 * Загружает и отображает полный список тегов галереи в боковой панели.
 * Пока панель закрыта, список не запрашивается: первая загрузка выполняется
 * при открытии панели, последующие - при каждом повторном открытии.
 */
const TagsOffcanvas = ({ show, onHide }: TagsOffcanvasProps) => {
  // При закрытой панели fetchFunction отдает пустой массив без сетевого запроса;
  // смена ссылки при переключении show запускает загрузку хуком
  const loadTags = useCallback(async () => {
    if (!show) {
      return [];
    }
    const data = await galleryService.getTags();
    return parseListResponse(data).items;
  }, [show]);

  const { data, loading, error, refetch } = useApiData(loadTags);
  const tags = data ?? [];

  /** Повторная загрузка тегов после ошибки. */
  const handleRetry = () => {
    refetch();
  };

  return (
    <Offcanvas show={show} onHide={onHide} placement="start">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Тэги</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {loading && <Spinner message="Загрузка тегов..." />}
        {error && (
          <AlertList
            messages={[
              {
                message: error,
                level: 'error',
                actions: (
                  <button className="btn btn-outline-primary btn-sm" onClick={handleRetry}>
                    Повторить
                  </button>
                ),
              },
            ]}
          />
        )}
        {!loading && !error && tags.length === 0 && (
          <AlertList messages={[{ message: 'Нет доступных тегов', level: 'info' }]} />
        )}
        {!loading && !error && tags.length > 0 && (
          <div className="d-grid gap-2">
            {tags.map((tag) => (
              <TagButton key={tag.id} tag={tag} />
            ))}
          </div>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default TagsOffcanvas;
