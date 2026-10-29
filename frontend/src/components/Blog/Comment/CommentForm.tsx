import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import { Editor } from '@tinymce/tinymce-react';
import AlertList from '@components/Alert/AlertList';
import { blogService } from '@services';
import { useHtmlTheme } from '@hooks';
import { getEditorInit } from '@components/Blog/utils/tinymce';
import { getErrorMessage } from '@utils/errors';
import { stripHtml } from '@components/Blog/utils/html';

/** Свойства формы добавления комментария. */
export interface CommentFormProps {
  /** ID статьи, к которой добавляется комментарий. */
  articleId: number;
  /** Авторизован ли текущий пользователь. */
  isAuthenticated: boolean;
  /** URL страницы входа с параметром next. */
  loginUrl: string;
  /** Callback успешной отправки формы. */
  onSuccess?: () => void;
  /** URL скрипта TinyMCE. */
  tinymceScriptSrc?: string;
  /** Дополнительные действия в ряду кнопки отправки. */
  asideActions?: React.ReactNode;
}

/**
 * Компонент формы добавления комментария с WYSIWYG редактором TinyMCE.
 *
 * Для авторизованных пользователей отображает форму с WYSIWYG редактором и
 * кнопкой отправки. Для неавторизованных - ссылку на страницу входа.
 * Использует сессионную аутентификацию Django (CSRF-токен из cookie).
 * Ресурсы TinyMCE загружаются по URL из пропа (STATIC_URL хранилища статики);
 * редактор следует теме сайта.
 *
 * @example
 * <CommentForm
 *   articleId={1}
 *   isAuthenticated={true}
 *   loginUrl="/accounts/login/?next=/blog/slug/"
 *   onSuccess={handleSuccess}
 * />
 */
const CommentForm = ({
  articleId,
  isAuthenticated,
  loginUrl,
  onSuccess,
  tinymceScriptSrc = '/static/tinymce/tinymce.min.js',
  asideActions = null,
}: CommentFormProps) => {
  /** Действующая тема сайта для перекраски редактора. */
  const htmlTheme = useHtmlTheme();

  /** Состояние текста комментария. */
  const [content, setContent] = useState('');

  /** Состояние отправки формы. */
  const [submitting, setSubmitting] = useState(false);

  /** Состояние ошибки при отправке. */
  const [error, setError] = useState<string | null>(null);

  if (!isAuthenticated) {
    return (
      <>
        <a className="btn btn-outline-dark" href={loginUrl}>
          Войдите, чтобы оставить комментарий
        </a>
        <br />
      </>
    );
  }

  /** Обработчик отправки формы. */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripHtml(content)) {
      setError('Комментарий не может быть пустым');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await blogService.createComment(articleId, { content });
      setContent('');
      onSuccess?.();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <AlertList messages={[{ message: error, level: 'error' }]} />}
      <div className="form-group">
        <Editor
          key={htmlTheme}
          tinymceScriptSrc={tinymceScriptSrc}
          value={content}
          onEditorChange={(newValue) => setContent(newValue)}
          disabled={submitting}
          init={getEditorInit(htmlTheme === 'dark')}
        />
        <br />
        <div className="d-flex align-items-center">
          <Button type="submit" variant="outline-dark" disabled={submitting}>
            {submitting ? 'Отправка...' : 'Добавить комментарий'}
            {!submitting && <i className="bi bi-chat-dots ms-1" />}
          </Button>
          {asideActions && <div className="ms-auto">{asideActions}</div>}
        </div>
      </div>
    </form>
  );
};

export default CommentForm;
