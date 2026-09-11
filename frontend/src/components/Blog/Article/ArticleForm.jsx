import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Card, Form } from 'react-bootstrap';
import { Editor } from '@tinymce/tinymce-react';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService, navigateTo } from '@services';
import { useHtmlTheme } from '@hooks';
import { getEditorInit } from '@utils/tinymce';

/**
 * Интервал автосохранения статьи в миллисекундах.
 * @type {number}
 */
const AUTOSAVE_INTERVAL_MS = 60000;

/**
 * Пустое состояние формы новой статьи.
 * @type {Object}
 */
const EMPTY_FORM = {
  title: '',
  description: '',
  content: '',
  categories: [],
  series: [],
  topics: [],
  imageFile: null,
  removeImage: false,
  isPublished: false,
};

/**
 * Удаляет HTML-теги и пробелы по краям для проверки содержимого на пустоту.
 * @param {string} html - HTML-строка
 * @return {string} Чистый текст
 */
const stripHtml = (html) => html.replace(/<[^>]*>/g, '').trim();

/**
 * Возвращает отпечаток выбранного файла для отслеживания изменений.
 * @param {File|null} file - Выбранный файл обложки
 * @return {string|null} Отпечаток файла или null
 */
const fileSignature = (file) => (file ? `${file.name}:${file.size}:${file.lastModified}` : null);

/**
 * Форматирует время для подписи автосохранения в виде ЧЧ:ММ.
 * @param {Date} date - Момент сохранения
 * @return {string} Время в формате ЧЧ:ММ
 */
const formatTime = (date) => date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

/**
 * Строит отпечаток состояния формы для сравнения при автосохранении.
 * @param {Object} state - Состояние формы
 * @return {string} JSON-отпечаток состояния
 */
const buildSnapshot = (state) =>
  JSON.stringify({
    title: state.title,
    description: state.description,
    content: state.content,
    categories: [...state.categories].sort((a, b) => a - b),
    series: [...state.series].sort((a, b) => a - b),
    topics: [...state.topics].sort((a, b) => a - b),
    image: fileSignature(state.imageFile),
    removeImage: state.removeImage,
    isPublished: state.isPublished,
  });

/**
 * Проверяет готовность формы к сохранению на сервере.
 * @param {Object} state - Состояние формы
 * @return {boolean} True, если обязательные поля заполнены
 */
const canSave = (state) => Boolean(state.title.trim()) && Boolean(stripHtml(state.content));

/**
 * Компонент формы создания и редактирования статьи с WYSIWYG редактором TinyMCE.
 *
 * Одна форма обслуживает страницы создания (/blog/article/create/) и редактирования
 * (/blog/<slug>/edit/): в режиме редактирования по articleId загружаются данные
 * статьи. Поддерживает автосохранение раз в минуту при наличии изменений:
 * для новой статьи первое автосохранение создает черновик, далее изменения
 * отправляются в ту же статью; автосохранение действует только на черновики -
 * опубликованная статья обновляется явной кнопкой "Сохранить". Статус
 * публикации меняют только явные кнопки, набор которых зависит от статуса
 * статьи: у черновика - "Сохранить черновик" и "Опубликовать", у опубликованной -
 * "Сохранить" и "Снять с публикации". Редактор TinyMCE следует теме сайта.
 * Ресурсы TinyMCE загружаются локально, без CDN и API-ключа.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {number|null} [props.articleId=null] - ID редактируемой статьи (null для новой)
 * @return {JSX.Element} Компонент формы статьи
 *
 * @example
 * // Создание статьи
 * <ArticleForm />
 *
 * @example
 * // Редактирование существующей статьи
 * <ArticleForm articleId={5} />
 */
const ArticleForm = ({ articleId = null }) => {
  /**
   * Действующая тема сайта для перекраски редактора
   * @type {[string, function]}
   */
  const htmlTheme = useHtmlTheme();

  /**
   * Состояние формы статьи
   * @type {[Object, function]}
   */
  const [form, setForm] = useState(EMPTY_FORM);

  /**
   * Справочники категорий, серий и тем для мультивыбора
   * @type {[Object, function]}
   */
  const [taxonomies, setTaxonomies] = useState({ categories: [], series: [], topics: [] });

  /**
   * URL текущей обложки статьи (только в режиме редактирования)
   * @type {[string|null, function]}
   */
  const [currentImage, setCurrentImage] = useState(null);

  /**
   * ID статьи после создания черновика автосохранением
   * @type {[number|null, function]}
   */
  const [savedArticleId, setSavedArticleId] = useState(articleId);

  /**
   * Состояние загрузки данных
   * @type {[boolean, function]}
   */
  const [loading, setLoading] = useState(true);

  /**
   * Состояние ошибки загрузки данных
   * @type {[string|null, function]}
   */
  const [loadError, setLoadError] = useState(null);

  /**
   * Состояние отправки формы
   * @type {[boolean, function]}
   */
  const [submitting, setSubmitting] = useState(false);

  /**
   * Состояние ошибки при явном сохранении
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

  /**
   * Подпись последнего автосохранения
   * @type {[string|null, function]}
   */
  const [autosaveStatus, setAutosaveStatus] = useState(null);

  /**
   * Признак ошибки автосохранения
   * @type {[boolean, function]}
   */
  const [autosaveError, setAutosaveError] = useState(false);

  /**
   * Ключ для перезапуска интервала автосохранения после явного сохранения
   * @type {[number, function]}
   */
  const [timerKey, setTimerKey] = useState(0);

  /**
   * Счетчик повторных попыток загрузки
   * @type {[number, function]}
   */
  const [retryCount, setRetryCount] = useState(0);

  /**
   * Отпечаток состояния на момент последнего сохранения
   * @type {Object} Ref
   */
  const snapshotRef = useRef(null);

  /**
   * Признак выполняемого запроса для блокировки автосохранения
   * @type {Object} Ref
   */
  const submittingRef = useRef(false);

  /**
   * Ссылка на последнюю версию обработчика автосохранения
   * @type {Object} Ref
   */
  const autosaveRef = useRef(() => {});

  /**
   * Признак инициализации отпечатка после загрузки данных
   * @type {Object} Ref
   */
  const snapshotInitializedRef = useRef(false);

  /**
   * Обновляет часть состояния формы
   * @function updateForm
   * @param {Object} patch - Изменяемые поля формы
   * @return {void}
   */
  const updateForm = (patch) => setForm((prev) => ({ ...prev, ...patch }));

  /**
   * Эффект загрузки справочников и данных статьи при монтировании
   */
  useEffect(() => {
    /**
     * Асинхронная загрузка данных формы
     * @async
     * @function load
     * @return {Promise<void>}
     */
    const load = async () => {
      setLoading(true);
      setLoadError(null);
      try {
        const [categoriesData, seriesData, topicsData] = await Promise.all([
          blogService.getCategories(),
          blogService.getSeries(),
          blogService.getTopics(),
        ]);
        setTaxonomies({
          categories: categoriesData.results || categoriesData,
          series: seriesData.results || seriesData,
          topics: topicsData.results || topicsData,
        });
        if (articleId) {
          const article = await blogService.getArticle(articleId);
          setForm({
            title: article.title,
            description: article.description || '',
            content: article.content,
            categories: (article.categories || []).map((item) => item.id),
            series: (article.series || []).map((item) => item.id),
            topics: (article.topics || []).map((item) => item.id),
            imageFile: null,
            removeImage: false,
            isPublished: article.public,
          });
          setCurrentImage(article.image || null);
          setSavedArticleId(article.id);
        }
      } catch (err) {
        setLoadError(err.message);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [articleId, retryCount]);

  /**
   * Фиксирует отпечаток исходного состояния формы после загрузки
   */
  useEffect(() => {
    if (!loading && !snapshotInitializedRef.current) {
      snapshotRef.current = buildSnapshot(form);
      snapshotInitializedRef.current = true;
    }
  }, [loading, form]);

  /**
   * Собирает FormData из состояния формы для отправки на сервер
   * @function buildFormData
   * @param {Object} state - Состояние формы
   * @return {FormData} Данные формы
   */
  const buildFormData = (state) => {
    const formData = new FormData();
    formData.append('title', state.title.trim());
    formData.append('description', state.description.trim());
    formData.append('content', state.content);
    formData.append('public', state.isPublished ? 'true' : 'false');
    ['categories', 'series', 'topics'].forEach((field) => {
      if (state[field].length > 0) {
        state[field].forEach((id) => formData.append(field, id));
      } else {
        formData.append(field, '');
      }
    });
    if (state.imageFile) {
      formData.append('image', state.imageFile);
    }
    if (state.removeImage && !state.imageFile) {
      formData.append('remove_image', 'true');
    }
    return formData;
  };

  /**
   * Сохраняет статью: создает черновик или обновляет существующую
   * @async
   * @function saveArticle
   * @param {Object} state - Состояние формы для сохранения
   * @return {Promise<Object>} Сохраненная статья в полном представлении
   */
  const saveArticle = async (state) => {
    const formData = buildFormData(state);
    const response = savedArticleId
      ? await blogService.updateArticle(savedArticleId, formData)
      : await blogService.createArticle(formData);
    if (!savedArticleId && response.id) {
      setSavedArticleId(response.id);
    }
    snapshotRef.current = buildSnapshot(state);
    return response;
  };

  /**
   * Обработчик автосохранения: сохраняет только при изменениях и только черновики
   * @async
   * @function handleAutosave
   * @return {Promise<void>}
   */
  const handleAutosave = async () => {
    if (loading || submittingRef.current || !canSave(form)) {
      return;
    }
    // Опубликованная статья обновляется только явной кнопкой "Сохранить":
    // черновик с правками читатели видеть не должны
    if (savedArticleId && form.isPublished) {
      return;
    }
    if (snapshotRef.current === buildSnapshot(form)) {
      return;
    }
    submittingRef.current = true;
    try {
      await saveArticle(form);
      setAutosaveError(false);
      setAutosaveStatus(`Автосохранено в ${formatTime(new Date())}`);
    } catch {
      setAutosaveError(true);
    } finally {
      submittingRef.current = false;
    }
  };

  /**
   * Эффект обновления ссылки на обработчик автосохранения
   */
  useEffect(() => {
    autosaveRef.current = handleAutosave;
  });

  /**
   * Эффект запуска интервала автосохранения
   */
  useEffect(() => {
    const interval = setInterval(() => autosaveRef.current(), AUTOSAVE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [timerKey]);

  /**
   * Обработчик явного сохранения с выбранным статусом публикации
   * @async
   * @function handleSave
   * @param {boolean} isPublished - Опубликовать статью или сохранить черновиком
   * @return {Promise<void>}
   */
  const handleSave = async (isPublished) => {
    setError(null);
    if (!form.title.trim()) {
      setError('Заполните заголовок статьи');
      return;
    }
    if (!stripHtml(form.content)) {
      setError('Заполните текст статьи');
      return;
    }
    setSubmitting(true);
    submittingRef.current = true;
    try {
      const response = await saveArticle({ ...form, isPublished });
      setTimerKey((key) => key + 1);
      navigateTo(response.url || `/blog/article/${response.slug}/`);
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
      submittingRef.current = false;
    }
  };

  /**
   * Обработчик сохранения черновика
   * @function handleSaveDraft
   * @return {void}
   */
  const handleSaveDraft = () => handleSave(false);

  /**
   * Обработчик публикации статьи
   * @function handlePublish
   * @return {void}
   */
  const handlePublish = () => handleSave(true);

  /**
   * Обработчик сохранения опубликованной статьи без смены статуса
   * @function handleSavePublished
   * @return {void}
   */
  const handleSavePublished = () => handleSave(true);

  /**
   * Обработчик снятия статьи с публикации
   * @function handleUnpublish
   * @return {void}
   */
  const handleUnpublish = () => handleSave(false);

  /**
   * Обработчик мультивыбора справочника
   * @function handleMultiSelect
   * @param {string} field - Поле формы (categories, series, topics)
   * @return {function(Event): void} Обработчик изменения
   */
  const handleMultiSelect = (field) => (event) => {
    const selected = Array.from(event.target.selectedOptions, (option) => Number(option.value));
    updateForm({ [field]: selected });
  };

  /**
   * Обработчик выбора файла обложки
   * @function handleImageChange
   * @param {Event} event - Событие изменения поля файла
   * @return {void}
   */
  const handleImageChange = (event) => {
    const file = event.target.files[0] || null;
    updateForm({ imageFile: file, removeImage: false });
  };

  /**
   * Обработчик повторной попытки загрузки данных
   * @function handleRetry
   * @return {void}
   */
  const handleRetry = () => setRetryCount((count) => count + 1);

  if (loading) {
    return <SpinnerComponent message="Загрузка формы..." />;
  }

  if (loadError) {
    return (
      <AlertList
        messages={[
          {
            message: loadError,
            level: 'error',
            actions: (
              <Button variant="outline-primary" size="sm" onClick={handleRetry}>
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow rounded">
        <Card.Body>
          <h1 className="card-title fs-4">{savedArticleId ? 'Редактирование статьи' : 'Новая статья'}</h1>
          {error && <AlertList messages={[{ message: error, level: 'error' }]} />}
          <Form>
            <Form.Group className="mb-3" controlId="article-title">
              <Form.Label>Заголовок</Form.Label>
              <Form.Control
                type="text"
                value={form.title}
                onChange={(event) => updateForm({ title: event.target.value })}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-description">
              <Form.Label>Краткое описание</Form.Label>
              <Form.Control
                type="text"
                value={form.description}
                onChange={(event) => updateForm({ description: event.target.value })}
                maxLength={255}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-content">
              <Form.Label>Содержание</Form.Label>
              <Editor
                key={htmlTheme}
                tinymceScriptSrc="/static/tinymce/tinymce.min.js"
                value={form.content}
                onEditorChange={(value) => updateForm({ content: value })}
                disabled={submitting}
                init={getEditorInit(htmlTheme === 'dark')}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-categories">
              <Form.Label>Категории</Form.Label>
              <Form.Select
                multiple
                size={5}
                value={form.categories}
                onChange={handleMultiSelect('categories')}
              >
                {taxonomies.categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-series">
              <Form.Label>Серии</Form.Label>
              <Form.Select
                multiple
                size={5}
                value={form.series}
                onChange={handleMultiSelect('series')}
              >
                {taxonomies.series.map((serie) => (
                  <option key={serie.id} value={serie.id}>
                    {serie.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-topics">
              <Form.Label>Темы</Form.Label>
              <Form.Select
                multiple
                size={5}
                value={form.topics}
                onChange={handleMultiSelect('topics')}
              >
                {taxonomies.topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-image">
              <Form.Label>Обложка</Form.Label>
              <Form.Control type="file" accept="image/*" onChange={handleImageChange} />
              {currentImage && !form.imageFile && (
                <>
                  {form.removeImage ? (
                    <div className="text-muted small mt-2">Обложка будет удалена после сохранения</div>
                  ) : (
                    <img
                      src={currentImage}
                      alt="Текущая обложка"
                      className="img-fluid mt-2"
                      style={{ maxHeight: '200px' }}
                    />
                  )}
                  <Form.Check
                    type="checkbox"
                    id="article-remove-image"
                    className="mt-2"
                    label="Убрать обложку"
                    checked={form.removeImage}
                    onChange={(event) => updateForm({ removeImage: event.target.checked })}
                  />
                </>
              )}
            </Form.Group>

            <div className="d-flex align-items-center">
              {Boolean(savedArticleId) && form.isPublished ? (
                <>
                  <Button variant="dark" onClick={handleSavePublished} disabled={submitting} className="me-2">
                    {submitting ? 'Сохранение...' : 'Сохранить'}
                  </Button>
                  <Button variant="outline-dark" onClick={handleUnpublish} disabled={submitting}>
                    {submitting ? 'Сохранение...' : 'Снять с публикации'}
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="dark" onClick={handleSaveDraft} disabled={submitting} className="me-2">
                    {submitting ? 'Сохранение...' : 'Сохранить черновик'}
                  </Button>
                  <Button variant="outline-dark" onClick={handlePublish} disabled={submitting}>
                    {submitting ? 'Публикация...' : 'Опубликовать'}
                  </Button>
                </>
              )}
              {(autosaveError || autosaveStatus) && (
                <small className={autosaveError ? 'text-danger ms-2' : 'text-muted ms-2'}>
                  {autosaveError ? 'Не удалось автосохранить' : autosaveStatus}
                </small>
              )}
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

ArticleForm.propTypes = {
  articleId: PropTypes.number,
};

export default ArticleForm;
