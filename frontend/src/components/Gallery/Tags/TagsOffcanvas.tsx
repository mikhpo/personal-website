import React, { useCallback, useEffect, useState } from 'react';
import { Offcanvas } from 'react-bootstrap';
import TagButton from '@components/Gallery/Tags/TagButton';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../../types/api-schema';

type Tag = components['schemas']['Tag'];

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
 */
const TagsOffcanvas = ({ show, onHide }: TagsOffcanvasProps) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Загружает список тегов из API и обновляет состояние компонента.
   *
   * Стабильность ссылки критична для корректной работы useEffect: функция
   * не меняется все время жизни компонента.
   */
  const loadTags = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await galleryService.getTags();
      const { items } = parseListResponse(data);

      setTags(items);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (show) {
      loadTags();
    }
  }, [show, loadTags]);

  /** Повторная загрузка тегов после ошибки. */
  const handleRetry = () => loadTags();

  return (
    <Offcanvas show={show} onHide={onHide} placement="start">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Тэги</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {loading && <SpinnerComponent message="Загрузка тегов..." />}
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
