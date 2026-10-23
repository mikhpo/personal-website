import React from 'react';
import { Card } from 'react-bootstrap';
import type { components } from '../../../types/api-schema';

type Article = components['schemas']['Article'];

/** Свойства компонента карточки статьи. */
export interface ArticleCardProps {
  article: Article;
}

/**
 * Компонент карточки статьи.
 *
 * Отображает превью статьи с заголовком и содержимым.
 * При длинном содержимом (более 200 слов) обрезает текст до 50 слов
 * и добавляет ссылку "Читать дальше".
 *
 * @example
 * <ArticleCard
 *   article={{
 *     id: 1,
 *     title: 'Введение в React Hooks',
 *     content: '<p>Текст статьи...</p>',
 *   }}
 * />
 */
const ArticleCard = ({ article }: ArticleCardProps) => {
  const articleUrl = article.url || `/blog/${article.id}/`;

  /** Признак длинного контента (более 200 слов). */
  const isLong = article.content && article.content.split(' ').length > 200;

  /** Усечённый HTML-контент для длинных статей (первые 50 слов). */
  const truncatedContent = isLong ? article.content.split(' ').slice(0, 50).join(' ') : article.content;

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow mb-4 rounded justify-content">
        <Card.Body>
          <h2 className="card-title fs-4">
            <a href={articleUrl}>{article.title}</a>
          </h2>
          <p className="card-text" dangerouslySetInnerHTML={{ __html: truncatedContent }} />
          {isLong && <a href={articleUrl}>Читать дальше</a>}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ArticleCard;
