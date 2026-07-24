import React, { useState, useEffect } from 'react';
import { Offcanvas } from 'react-bootstrap';
import PropTypes from 'prop-types';
import TagButton from '@components/Gallery/Tags/TagButton';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';

/**
 * Компонент боковой панели с тегами.
 *
 * Загружает и отображает список всех тегов галереи в боковой панели.
 *
 * @param {Object} props - Пропсы компонента
 * @param {boolean} props.show - Показывать ли панель
 * @param {Function} props.onHide - Обработчик закрытия панели
 * @param {string} [props.tagsApiUrl="/api/gallery/tags/"] - URL API для загрузки тегов
 * @return {JSX.Element} Компонент боковой панели с тегами
 */
const TagsOffcanvas = ({ show, onHide, tagsApiUrl = '/api/gallery/tags/' }) => {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!show) return;

    let isMounted = true;

    /**
     * Загружает список тегов из API и обновляет состояние компонента.
     *
     * Выполняет HTTP-запрос к API галереи для получения списка всех тегов.
     * Устанавливает состояние загрузки перед запросом и обрабатывает ошибки.
     * Использует флаг isMounted для предотвращения обновления состояния после размонтирования.
     *
     * @async
     * @function loadTags
     * @return {Promise<void>} Промис, который разрешается после успешной загрузки тегов
     * @throws {Error} Бросает ошибку при неудачном HTTP-запросе
     */
    const loadTags = async () => {
      try {
        if (!isMounted) return;

        setLoading(true);
        setError(null);

        const response = await fetch(tagsApiUrl);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }

        const data = await response.json();
        const tagsList = data.results || data;

        if (isMounted) {
          setTags(Array.isArray(tagsList) ? tagsList : []);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    };

    loadTags();

    return () => {
      isMounted = false;
    };
  }, [show, tagsApiUrl]);

  /**
   * Обработчик повторной попытки загрузки тегов после ошибки.
   *
   * Создает новую функцию загрузки с собственным флагом isMounted для предотвращения
   * утечек памяти. Сбрасывает состояние ошибки и запускает повторную загрузку тегов.
   * Возвращает функцию очистки для предотвращения обновления состояния после размонтирования.
   *
   * @function handleRetry
   * @return {Function} Функция очистки для предотвращения утечек памяти
   */
  const handleRetry = () => {
    let isMounted = true;

    /**
     * Повторно загружает список тегов из API после ошибки пользователя.
     *
     * Выполняет те же действия, что и loadTags: отправляет HTTP-запрос к API,
     * обрабатывает ответ и обновляет состояние компонента. Используется при
     * нажатии пользователем кнопки "Повторить" после неудачной загрузки.
     *
     * @async
     * @function retryLoadTags
     * @return {Promise<void>} Промис, который разрешается после успешной загрузки тегов
     * @throws {Error} Бросает ошибку при неудачном HTTP-запросе
     */
    const retryLoadTags = async () => {
      try {
        if (!isMounted) return;

        setLoading(true);
        setError(null);

        const response = await fetch(tagsApiUrl);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }

        const data = await response.json();
        const tagsList = data.results || data;

        if (isMounted) {
          setTags(Array.isArray(tagsList) ? tagsList : []);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
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
                  <button
                    className="btn btn-outline-primary btn-sm"
                    onClick={handleRetry}
                  >
                    Повторить
                  </button>
                )
              }
            ]}
          />
        )}
        {!loading && !error && tags.length === 0 && (
          <AlertList messages={[{ message: "Нет доступных тегов", level: "info" }]} />
        )}
        {!loading && !error && tags.length > 0 && (
          <div className="d-grid gap-2">
            {tags.map(tag => (
              <TagButton key={tag.id} tag={tag} />
            ))}
          </div>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
};

TagsOffcanvas.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  tagsApiUrl: PropTypes.string,
};

export default TagsOffcanvas;
