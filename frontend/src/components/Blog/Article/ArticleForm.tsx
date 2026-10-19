import React, { useEffect, useRef, useState } from 'react';
import { Button, Card, Form } from 'react-bootstrap';
import { Editor } from '@tinymce/tinymce-react';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService, navigateTo } from '@services';
import { useHtmlTheme } from '@hooks';
import { getEditorInit } from '@utils/tinymce';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../../types/api-schema';
import type { Paginated } from '../../../types/pagination';

type Article = components['schemas']['Article'];
type Category = components['schemas']['Category'];
type Series = components['schemas']['Series'];
type Topic = components['schemas']['Topic'];

/** Интервал автосохранения статьи в миллисекундах. */
const AUTOSAVE_INTERVAL_MS = 60000;

/** Состояние формы статьи. */
interface ArticleFormState {
  title: string;
  description: string;
  content: string;
  categories: number[];
  series: number[];
  topics: number[];
  imageFile: File | null;
  removeImage: boolean;
  isPublished: boolean;
}

/** Пустое состояние формы новой статьи. */
const EMPTY_FORM: ArticleFormState = {
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

/** Справочники категорий, серий и тем для мультивыбора. */
interface Taxonomies {
  categories: Category[];
  series: Series[];
  topics: Topic[];
}

/**
 * Удаляет HTML-теги и пробелы по краям для проверки содержимого на пустоту.
 */
const stripHtml = (html: string): string => html.replace(/<[^>]*>/g, '').trim();

/**
 * Возвращает отпечаток выбранного файла для отслеживания изменений.
 */
const fileSignature = (file: File | null): string | null =>
  file ? `${file.name}:${file.size}:${file.lastModified}` : null;

/**
 * Форматирует время для подписи автосохранения в виде ЧЧ:ММ.
 */
const formatTime = (date: Date): string => date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

/**
 * Строит отпечаток состояния формы для сравнения при автосохранении.
 */
const buildSnapshot = (state: ArticleFormState): string =>
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
 */
const canSave = (state: ArticleFormState): boolean => Boolean(state.title.trim()) && Boolean(stripHtml(state.content));

/** Свойства формы статьи. */
export interface ArticleFormProps {
  /** ID редактируемой статьи; null для новой. */
  articleId?: number | null;
  /** URL скрипта TinyMCE. */
  tinymceScriptSrc?: string;
}

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
 * URL скрипта TinyMCE передается из шаблона (STATIC_URL хранилища статики).
 *
 * @example
 * <ArticleForm />
 *
 * @example
 * <ArticleForm articleId={5} />
 */
const ArticleForm = ({ articleId = null, tinymceScriptSrc = '/static/tinymce/tinymce.min.js' }: ArticleFormProps) => {
  /** Действующая тема сайта для перекраски редактора. */
  const htmlTheme = useHtmlTheme();

  /** Состояние формы статьи. */
  const [form, setForm] = useState<ArticleFormState>(EMPTY_FORM);

  /** Справочники категорий, серий и тем для мультивыбора. */
  const [taxonomies, setTaxonomies] = useState<Taxonomies>({ categories: [], series: [], topics: [] });

  /** URL текущей обложки статьи (только в режиме редактирования). */
  const [currentImage, setCurrentImage] = useState<string | null>(null);

  /** ID статьи после создания черновика автосохранением. */
  const [savedArticleId, setSavedArticleId] = useState<number | null>(articleId);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(true);

  /** Состояние ошибки загрузки данных. */
  const [loadError, setLoadError] = useState<string | null>(null);

  /** Состояние отправки формы. */
  const [submitting, setSubmitting] = useState(false);

  /** Состояние ошибки при явном сохранении. */
  const [error, setError] = useState<string | null>(null);

  /** Подпись последнего автосохранения. */
  const [autosaveStatus, setAutosaveStatus] = useState<string | null>(null);

  /** Признак ошибки автосохранения. */
  const [autosaveError, setAutosaveError] = useState(false);

  /** Ключ для перезапуска интервала автосохранения после явного сохранения. */
  const [timerKey, setTimerKey] = useState(0);

  /** Счетчик повторных попыток загрузки. */
  const [retryCount, setRetryCount] = useState(0);

  /** Отпечаток состояния на момент последнего сохранения. */
  const snapshotRef = useRef<string | null>(null);

  /** Зеркало ID статьи: сохранение читает его без зависимости от момента рендера. */
  const savedArticleIdRef = useRef<number | null>(articleId);

  /** Зеркало состояния формы: явное сохранение после ожидания автосохранения строит данные по свежему состоянию. */
  const formRef = useRef<ArticleFormState>(EMPTY_FORM);

  /** Промис выполняемого автосохранения: явное сохранение дожидается его завершения. */
  const autosaveInFlightRef = useRef<Promise<void> | null>(null);

  /** Признак выполняемого запроса для блокировки автосохранения. */
  const submittingRef = useRef(false);

  /** Ссылка на последнюю версию обработчика автосохранения. */
  const autosaveRef = useRef<() => void>(() => {});

  /** Признак инициализации отпечатка после загрузки данных. */
  const snapshotInitializedRef = useRef(false);

  /** Обновляет часть состояния формы. */
  const updateForm = (patch: Partial<ArticleFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  /**
   * Загружает справочник целиком, проходя все страницы пагинации.
   */
  const fetchTaxonomy = async <T,>(fetchPage: (params: { page: number }) => Promise<Paginated<T>>): Promise<T[]> => {
    const items: T[] = [];
    // Ограничение итераций защищает от зацикливания при некорректном API
    for (let page = 1; page <= 100; page += 1) {
      const { items: pageItems, next } = parseListResponse(await fetchPage({ page }));
      items.push(...pageItems);
      if (!next) {
        return items;
      }
    }
    return items;
  };

  // Эффект загрузки справочников и данных статьи при монтировании
  useEffect(() => {
    /** Асинхронная загрузка данных формы. */
    const load = async () => {
      setLoading(true);
      setLoadError(null);
      try {
        const [categoriesData, seriesData, topicsData] = await Promise.all([
          fetchTaxonomy<Category>(blogService.getCategories),
          fetchTaxonomy<Series>(blogService.getSeries),
          fetchTaxonomy<Topic>(blogService.getTopics),
        ]);
        setTaxonomies({
          categories: categoriesData,
          series: seriesData,
          topics: topicsData,
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
            isPublished: article.public ?? false,
          });
          setCurrentImage(article.image || null);
          savedArticleIdRef.current = article.id;
          setSavedArticleId(article.id);
        }
      } catch (err) {
        setLoadError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [articleId, retryCount]);

  // Эффект синхронизации зеркала состояния формы
  useEffect(() => {
    formRef.current = form;
  });

  /** Фиксирует отпечаток исходного состояния формы после загрузки. */
  useEffect(() => {
    if (!loading && !snapshotInitializedRef.current) {
      snapshotRef.current = buildSnapshot(form);
      snapshotInitializedRef.current = true;
    }
  }, [loading, form]);

  /**
   * Собирает FormData из состояния формы для отправки на сервер.
   */
  const buildFormData = (state: ArticleFormState): FormData => {
    const formData = new FormData();
    formData.append('title', state.title.trim());
    formData.append('description', state.description.trim());
    formData.append('content', state.content);
    formData.append('public', state.isPublished ? 'true' : 'false');
    (['categories', 'series', 'topics'] as const).forEach((field) => {
      if (state[field].length > 0) {
        state[field].forEach((id) => formData.append(field, String(id)));
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
   * Сохраняет статью: создает черновик или обновляет существующую.
   */
  const saveArticle = async (state: ArticleFormState): Promise<Article> => {
    const id = savedArticleIdRef.current;
    const formData = buildFormData(state);
    const response = id ? await blogService.updateArticle(id, formData) : await blogService.createArticle(formData);
    if (!id && response.id) {
      savedArticleIdRef.current = response.id;
      setSavedArticleId(response.id);
    }
    snapshotRef.current = buildSnapshot(state);
    return response;
  };

  /**
   * Обработчик автосохранения: сохраняет только при изменениях и только черновики.
   */
  const handleAutosave = async (): Promise<void> => {
    if (loading || submittingRef.current || !canSave(form)) {
      return;
    }
    // Опубликованная статья обновляется только явной кнопкой "Сохранить":
    // черновик с правками читатели видеть не должны
    if (savedArticleIdRef.current && form.isPublished) {
      return;
    }
    if (snapshotRef.current === buildSnapshot(form)) {
      return;
    }
    submittingRef.current = true;
    const savePromise = (async () => {
      try {
        await saveArticle(form);
        setAutosaveError(false);
        setAutosaveStatus(`Автосохранено в ${formatTime(new Date())}`);
      } catch {
        setAutosaveError(true);
      } finally {
        submittingRef.current = false;
        autosaveInFlightRef.current = null;
      }
    })();
    autosaveInFlightRef.current = savePromise;
    await savePromise;
  };

  // Эффект обновления ссылки на обработчик автосохранения
  useEffect(() => {
    autosaveRef.current = handleAutosave;
  });

  // Эффект запуска интервала автосохранения
  useEffect(() => {
    const interval = setInterval(() => autosaveRef.current(), AUTOSAVE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [timerKey]);

  /**
   * Обработчик явного сохранения с выбранным статусом публикации.
   */
  const handleSave = async (isPublished: boolean): Promise<void> => {
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
      // Дождаться выполняемого автосохранения: параллельные запросы с разным
      // public перезаписали бы результат друг друга
      if (autosaveInFlightRef.current) {
        await autosaveInFlightRef.current;
        submittingRef.current = true;
      }
      const response = await saveArticle({ ...formRef.current, isPublished });
      setTimerKey((key) => key + 1);
      navigateTo(response.url || `/blog/article/${response.slug}/`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
      submittingRef.current = false;
    }
  };

  /** Обработчик сохранения черновика. */
  const handleSaveDraft = () => handleSave(false);

  /** Обработчик публикации статьи. */
  const handlePublish = () => handleSave(true);

  /** Обработчик сохранения опубликованной статьи без смены статуса. */
  const handleSavePublished = () => handleSave(true);

  /** Обработчик снятия статьи с публикации. */
  const handleUnpublish = () => handleSave(false);

  /**
   * Обработчик мультивыбора справочника.
   */
  const handleMultiSelect =
    (field: 'categories' | 'series' | 'topics') => (event: React.ChangeEvent<HTMLSelectElement>) => {
      const selected = Array.from(event.target.selectedOptions, (option) => Number(option.value));
      updateForm({ [field]: selected } as Partial<ArticleFormState>);
    };

  /** Обработчик выбора файла обложки. */
  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    updateForm({ imageFile: file, removeImage: false });
  };

  /** Обработчик повторной попытки загрузки данных. */
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
                tinymceScriptSrc={tinymceScriptSrc}
                value={form.content}
                onEditorChange={(value) => updateForm({ content: value })}
                disabled={submitting}
                init={getEditorInit(htmlTheme === 'dark')}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="article-categories">
              <Form.Label>Категории</Form.Label>
              {/* size={5} исторически превращался в класс form-select-5, а не в нативный
                  атрибут размера, а числа в value не совпадали со строковыми option;
                  приведения сохраняют прежний DOM (журнал tasks.md, фаза 5) */}
              <Form.Select
                multiple
                size={5 as unknown as 'sm'}
                value={form.categories as unknown as readonly string[]}
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
                size={5 as unknown as 'sm'}
                value={form.series as unknown as readonly string[]}
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
                size={5 as unknown as 'sm'}
                value={form.topics as unknown as readonly string[]}
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

export default ArticleForm;
