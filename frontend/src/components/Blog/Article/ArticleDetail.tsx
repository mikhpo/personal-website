import React, { useEffect, useState } from 'react';
import { Card, Button } from 'react-bootstrap';
import CommentList from '@components/Blog/Comment/CommentList';
import CommentForm from '@components/Blog/Comment/CommentForm';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService } from '@services';
import type { components } from '@api-types/api-schema';

type Article = components['schemas']['Article'];

/** Свойства компонента детального просмотра статьи. */
export interface ArticleDetailProps {
  /** ID статьи (первичный ключ) для URL API. */
  articleId: number;
  /** Авторизован ли текущий пользователь. */
  isAuthenticated: boolean;
  /** URL страницы входа с параметром next. */
  loginUrl: string;
  /** Является ли текущий пользователь администратором. */
  isStaff?: boolean;
  /** URL скрипта TinyMCE. */
  tinymceScriptSrc?: string;
}

/**
 * Компонент детального просмотра статьи с комментариями.
 *
 * Отображает полный текст статьи, даты публикации и обновления, а также секцию
 * комментариев. Форма добавления комментария отображается только для
 * авторизованных пользователей. Для администраторов отображается кнопка
 * перехода к редактированию в ряду кнопки добавления комментария.
 *
 * @example
 * <ArticleDetail
 *   articleId={1}
 *   isAuthenticated={true}
 *   loginUrl="/accounts/login/?next=/blog/1/"
 * />
 */
const ArticleDetail = ({
  articleId,
  isAuthenticated,
  loginUrl,
  isStaff = false,
  tinymceScriptSrc = '/static/tinymce/tinymce.min.js',
}: ArticleDetailProps) => {
  /** Состояние статьи. */
  const [article, setArticle] = useState<Article | null>(null);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(true);

  /** Состояние ошибки при загрузке данных. */
  const [error, setError] = useState<string | null>(null);

  // Эффект для загрузки статьи при монтировании компонента
  useEffect(() => {
    /** Загружает статью из API. */
    const loadArticle = async () => {
      try {
        const data = await blogService.getArticle(articleId);
        setArticle(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    loadArticle();
  }, [articleId]);

  /**
   * Перезагружает статью после успешного добавления комментария
   * для обновления списка комментариев.
   */
  const handleCommentSuccess = async () => {
    setLoading(true);
    try {
      const data = await blogService.getArticle(articleId);
      setArticle(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  /** Повторная загрузка статьи. */
  const handleRetry = () => {
    /** Повторно загружает статью из API. */
    const retryLoad = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await blogService.getArticle(articleId);
        setArticle(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    retryLoad();
  };

  // Отображение индикатора загрузки
  if (loading) {
    return <Spinner message="Загрузка статьи..." />;
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
              <Button variant="outline-primary" size="sm" onClick={handleRetry}>
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  // Отображение сообщения если статья не найдена
  if (!article) {
    return <AlertList messages={[{ message: 'Статья не найдена', level: 'warning' }]} />;
  }

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow rounded justify-content">
        <Card.Body>
          <h1 className="card-title fs-4">{article.title}</h1>
          <p className="card-text" dangerouslySetInnerHTML={{ __html: article.content }} />
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
            tinymceScriptSrc={tinymceScriptSrc}
            asideActions={
              isStaff ? (
                <a className="btn btn-outline-dark btn-sm" href={`${article.url}edit/`}>
                  <i className="bi bi-pencil me-1" />
                  Редактировать
                </a>
              ) : null
            }
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

export default ArticleDetail;
