import React, { useEffect, useState } from 'react';
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
 * Загружает и отображает список всех тегов галереи в боковой панели.
 */
const TagsOffcanvas = ({ show, onHide }: TagsOffcanvasProps) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!show) return;

    let isMounted = true;

    /**
     * Загружает список тегов из API и обновляет состояние компонента.
     * Флаг isMounted предотвращает обновление состояния после размонтирования.
     */
    const loadTags = async () => {
      try {
        if (!isMounted) return;

        setLoading(true);
        setError(null);

        const data = await galleryService.getTags();
        const { items } = parseListResponse(data);

        if (isMounted) {
          setTags(items);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : String(err));
          setLoading(false);
        }
      }
    };

    loadTags();

    return () => {
      isMounted = false;
    };
  }, [show]);

  /**
   * Повторная загрузка тегов после ошибки с собственным флагом isMounted
   * для предотвращения утечек памяти.
   */
  const handleRetry = () => {
    let isMounted = true;

    /** Повторно загружает список тегов из API. */
    const retryLoadTags = async () => {
      try {
        if (!isMounted) return;

        setLoading(true);
        setError(null);

        const data = await galleryService.getTags();
        const { items } = parseListResponse(data);

        if (isMounted) {
          setTags(items);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : String(err));
          setLoading(false);
        }
      }
    };

    retryLoadTags();

    return () => {
      isMounted = false;
    };
  };

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
