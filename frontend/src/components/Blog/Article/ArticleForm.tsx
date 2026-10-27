import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Button, Card, Form } from 'react-bootstrap';
import { Editor } from '@tinymce/tinymce-react';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import MultiSelect from '@components/Blog/Article/MultiSelect';
import { blogService, navigateTo } from '@services';
import { useApiData, useArticleAutosave, useHtmlTheme } from '@hooks';
import { getEditorInit } from '@utils/tinymce';
import { getErrorMessage } from '@utils/errors';
import { stripHtml } from '@utils/html';
import type { components } from '@api-types/api-schema';

type Article = components['schemas']['Article'];
type Category = components['schemas']['Category'];
type Series = components['schemas']['Series'];
type Topic = components['schemas']['Topic'];

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

/** Данные формы: справочники и статья при редактировании. */
interface ArticleFormData {
  categories: Category[];
  series: Series[];
  topics: Topic[];
  article: Article | null;
}

/**
 * Возвращает отпечаток выбранного файла для отслеживания изменений.
 */
const fileSignature = (file: File | null): string | null =>
  file ? `${file.name}:${file.size}:${file.lastModified}` : null;

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

  /** URL текущей обложки статьи (только в режиме редактирования). */
  const [currentImage, setCurrentImage] = useState<string | null>(null);

  /** ID статьи после создания черновика автосохранением. */
  const [savedArticleId, setSavedArticleId] = useState<number | null>(articleId);

  /** Состояние отправки формы. */
  const [submitting, setSubmitting] = useState(false);

  /** Состояние ошибки при явном сохранении. */
  const [error, setError] = useState<string | null>(null);

  /** Заполнена ли форма загруженными данными; до этого автосохранение не инициализирует отпечаток. */
  const [formLoaded, setFormLoaded] = useState(false);

  /** Зеркало ID статьи: сохранение читает его без зависимости от момента рендера. */
  const savedArticleIdRef = useRef<number | null>(articleId);

  /** Зеркало состояния формы: явное сохранение после ожидания автосохранения строит данные по свежему состоянию. */
  const formRef = useRef<ArticleFormState>(EMPTY_FORM);

  /** Обновляет часть состояния формы. */
  const updateForm = (patch: Partial<ArticleFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  /**
   * Загружает справочники и данные статьи; при создании статьи article равен null.
   */
  const loadFormData = useCallback(async (): Promise<ArticleFormData> => {
    const [categories, series, topics] = await Promise.all([
      blogService.getCategories(),
      blogService.getSeries(),
      blogService.getTopics(),
    ]);
    const article = articleId ? await blogService.getArticle(articleId) : null;
    return { categories, series, topics, article };
  }, [articleId]);

  const { data, loading, error: loadError, refetch } = useApiData(loadFormData);

  // Эффект заполнения формы загруженными данными статьи
  useEffect(() => {
    if (!data) {
      return;
    }

    /** Заполняет форму данными загруженной статьи. */
    const fill = async () => {
      const { article } = data;
      if (article) {
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
        setSavedArticleId(article.id);
      }
      setFormLoaded(true);
    };

    fill();
  }, [data]);

  // Эффект синхронизации зеркала состояния формы
  useEffect(() => {
    formRef.current = form;
  });

  // Эффект синхронизации зеркала ID статьи
  useEffect(() => {
    savedArticleIdRef.current = savedArticleId;
  }, [savedArticleId]);

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
    return response;
  };

  // Автосохранение действует только на черновики: опубликованная статья
  // обновляется явной кнопкой "Сохранить"
  const autosaveEnabled = !(savedArticleId !== null && form.isPublished);

  /** Механика автосохранения: интервал, отпечаток, блокировки. */
  const { autosaveStatus, autosaveError, inFlightRef, submittingRef, restartTimer, markSaved } = useArticleAutosave({
    form,
    loading: loading || !formLoaded,
    enabled: autosaveEnabled,
    canSave: canSave(form),
    buildSnapshot,
    saveArticle,
  });

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
      if (inFlightRef.current) {
        await inFlightRef.current;
        submittingRef.current = true;
      }
      const state = { ...formRef.current, isPublished };
      const response = await saveArticle(state);
      markSaved(state);
      restartTimer();
      navigateTo(response.url || `/blog/article/${response.slug}/`);
    } catch (err) {
      setError(getErrorMessage(err));
      setSubmitting(false);
      submittingRef.current = false;
    }
  };

  /**
   * Обработчик выбора файла обложки.
   */
  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    updateForm({ imageFile: file, removeImage: false });
  };

  /** Обработчик повторной попытки загрузки данных. */
  const handleRetry = () => {
    refetch();
  };

  if (loading) {
    return <Spinner message="Загрузка формы..." />;
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

  const categories = data?.categories ?? [];
  const series = data?.series ?? [];
  const topics = data?.topics ?? [];

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

            <MultiSelect
              controlId="article-categories"
              label="Категории"
              options={categories}
              selected={form.categories}
              onChange={(selected) => updateForm({ categories: selected })}
            />

            <MultiSelect
              controlId="article-series"
              label="Серии"
              options={series}
              selected={form.series}
              onChange={(selected) => updateForm({ series: selected })}
            />

            <MultiSelect
              controlId="article-topics"
              label="Темы"
              options={topics}
              selected={form.topics}
              onChange={(selected) => updateForm({ topics: selected })}
            />

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
                  <Button variant="dark" onClick={() => handleSave(true)} disabled={submitting} className="me-2">
                    {submitting ? 'Сохранение...' : 'Сохранить'}
                  </Button>
                  <Button variant="outline-dark" onClick={() => handleSave(false)} disabled={submitting}>
                    {submitting ? 'Сохранение...' : 'Снять с публикации'}
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="dark" onClick={() => handleSave(false)} disabled={submitting} className="me-2">
                    {submitting ? 'Сохранение...' : 'Сохранить черновик'}
                  </Button>
                  <Button variant="outline-dark" onClick={() => handleSave(true)} disabled={submitting}>
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
