import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Form, Button } from 'react-bootstrap';
import AlertList from '@components/Alert/AlertList';

/**
 * Читает значение cookie по имени.
 *
 * @function getCookie
 * @param {string} name - Имя cookie
 * @return {string|null} Значение cookie или null
 */
const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

/**
 * Компонент формы добавления комментария.
 *
 * Для авторизованных пользователей отображает форму с полем ввода и кнопкой отправки.
 * Для неавторизованных — ссылку на страницу входа.
 * Использует сессионную аутентификацию Django (CSRF-токен из cookie).
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

    if (!content.trim()) {
      setError('Комментарий не может быть пустым');
      return;
    }

    setSubmitting(true);
    setError(null);

    const csrfToken = getCookie('csrftoken');

    try {
      const response = await fetch('/api/blog/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          article: articleId,
          content,
        }),
      });

      if (!response.ok) {
        throw new Error('Ошибка отправки комментария');
      }

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
        <Form.Control
          as="textarea"
          rows={3}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={submitting}
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