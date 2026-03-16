import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, Button } from 'react-bootstrap';
import CommentList from '@components/Blog/Comment/CommentList';
import CommentForm from '@components/Blog/Comment/CommentForm';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';

/**
 * Компонент детального просмотра статьи с комментариями.
 *
 * Отображает полный текст статьи, даты публикации и обновления, а также секцию комментариев.
 * Форма добавления комментария отображается только для авторизованных пользователей.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {number} props.articleId - ID статьи (первичный ключ) для URL API
 * @param {boolean} props.isAuthenticated - Авторизован ли текущий пользователь
 * @param {string} props.loginUrl - URL страницы входа с параметром next
 * @return {JSX.Element} Компонент детального просмотра статьи
 *
 * @example
 * // Использование компонента
 * <ArticleDetail
 *   articleId={1}
 *   isAuthenticated={true}
 *   loginUrl="/accounts/login/?next=/blog/1/"
 * />
 */
const ArticleDetail = ({ articleId, isAuthenticated, loginUrl }) => {
  /**
   * Состояние статьи
   * @type {[Object|null, function]}
   */
  const [article, setArticle] = useState(null);

  /**
   * Состояние загрузки данных
   * @type {[boolean, function]}
   */
  const [loading, setLoading] = useState(true);

  /**
   * Состояние ошибки при загрузке
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

  const url = `/api/blog/articles/${articleId}/`;

  /**
   * Эффект для загрузки статьи при монтировании компонента
   */
  useEffect(() => {
    /**
     * Асинхронная функция для загрузки статьи из API
     * @async
     * @function loadArticle
     * @return {Promise<void>}
     */
    const loadArticle = async () => {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Статья не найдена');
        }
        const data = await response.json();
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadArticle();
  }, [url]);

  /**
   * Обработчик успешного добавления комментария
   * Перезагружает статью для обновления списка комментариев
   * @async
   * @function handleCommentSuccess
   * @return {Promise<void>}
   */
  const handleCommentSuccess = async () => {
    setLoading(true);
    try {
      const response = await fetch(url);
      const data = await response.json();
      setArticle(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Обработчик повторной попытки загрузки
   * @function handleRetry
   * @return {void}
   */
  const handleRetry = () => {
    /**
     * Асинхронная функция для повторной загрузки статьи из API
     * @async
     * @function retryLoad
     * @return {Promise<void>}
     */
    const retryLoad = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Статья не найдена');
        }
        const data = await response.json();
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    retryLoad();
  };

  // Отображение индикатора загрузки
  if (loading) {
    return <SpinnerComponent message="Загрузка статьи..." />;
  }

  // Отображение сообщения об ошибке с кнопкой повтора
  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: 'error',
            actions: (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={handleRetry}
              >
                Повторить
              </Button>
            )
          }
        ]}
      />
    );
  }

  // Отображение сообщения если статья не найдена
  if (!article) {
    return <AlertList messages={[{ message: "Статья не найдена", level: "warning" }]} />;
  }

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow bg-white rounded justify-content">
        <Card.Body>
          <h4 className="card-title">{article.title}</h4>
          <p
            className="card-text"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
          <div className="card-footer">
            <small className="text-muted">Опубликовано {article.published_at}</small>
            <br />
            <small className="text-muted">Обновлено {article.modified_at}</small>
          </div>
        </Card.Body>

        <div id="comments_section">
          <CommentForm
            articleId={article.id}
            isAuthenticated={isAuthenticated}
            loginUrl={loginUrl}
            onSuccess={handleCommentSuccess}
          />
          {article.comments && article.comments.length > 0 && (
            <>
              <br />
              <CommentList comments={article.comments} />
            </>
          )}
        </div>
      </Card>
    </div>
  );
};

ArticleDetail.propTypes = {
  articleId: PropTypes.number.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  loginUrl: PropTypes.string.isRequired,
};

export default ArticleDetail;