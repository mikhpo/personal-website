import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Button } from 'react-bootstrap';
import { Editor } from '@tinymce/tinymce-react';
import AlertList from '@components/Alert/AlertList';
import { blogService } from '@services';
import { useHtmlTheme } from '@hooks';
import { getEditorInit } from '@utils/tinymce';

/**
 * Компонент формы добавления комментария с WYSIWYG редактором TinyMCE.
 *
 * Для авторизованных пользователей отображает форму с WYSIWYG редактором и кнопкой отправки.
 * Для неавторизованных - ссылку на страницу входа.
 * Использует сессионную аутентификацию Django (CSRF-токен из cookie).
 * Все ресурсы TinyMCE загружаются локально, без использования CDN и API-ключа;
 * редактор следует теме сайта.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {number} props.articleId - ID статьи, к которой добавляется комментарий
 * @param {boolean} props.isAuthenticated - Авторизован ли текущий пользователь
 * @param {string} props.loginUrl - URL страницы входа с параметром next
 * @param {function} [props.onSuccess] - Callback успешной отправки формы
 * @return {JSX.Element} Компонент формы комментария
 *
 * @example
 * // Авторизованный пользователь
 * <CommentForm articleId={1} isAuthenticated={true} loginUrl="/accounts/login/?next=/blog/slug/" onSuccess={handleSuccess} />
 *
 * @example
 * // Неавторизованный пользователь
 * <CommentForm articleId={1} isAuthenticated={false} loginUrl="/accounts/login/?next=/blog/slug/" />
 */
const CommentForm = ({ articleId, isAuthenticated, loginUrl, onSuccess }) => {
  /**
   * Действующая тема сайта для перекраски редактора
   * @type {[string, function]}
   */
  const htmlTheme = useHtmlTheme();

  /**
   * Состояние текста комментария
   * @type {[string, function]}
   */
  const [content, setContent] = useState('');

  /**
   * Состояние отправки формы
   * @type {[boolean, function]}
   */
  const [submitting, setSubmitting] = useState(false);

  /**
   * Состояние ошибки при отправке
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

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

  /**
   * Обработчик отправки формы
   * @async
   * @function handleSubmit
   * @param {Event} e - Событие отправки формы
   * @return {Promise<void>}
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Удаляем HTML-теги для проверки пустого содержимого
    const plainText = content.replace(/<[^>]*>/g, '').trim();
    if (!plainText) {
      setError('Комментарий не может быть пустым');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await blogService.createComment(articleId, { content });
      setContent('');
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <AlertList
          messages={[{ message: error, level: 'error' }]}
        />
      )}
      <div className="form-group">
        <Editor
          key={htmlTheme}
          tinymceScriptSrc="/static/tinymce/tinymce.min.js"
          value={content}
          onEditorChange={(newValue) => setContent(newValue)}
          disabled={submitting}
          init={getEditorInit(htmlTheme === 'dark')}
        />
        <br />
        <Button
          type="submit"
          variant="outline-dark"
          disabled={submitting}
        >
          {submitting ? 'Отправка...' : 'Добавить комментарий'}
          {!submitting && <i className="fas fa-comments ms-1" />}
        </Button>
      </div>
    </form>
  );
};

CommentForm.propTypes = {
  articleId: PropTypes.number.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  loginUrl: PropTypes.string.isRequired,
  onSuccess: PropTypes.func,
};

export default CommentForm;
