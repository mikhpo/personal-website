import React from 'react';
import { Card } from 'react-bootstrap';
import { stripHtml } from '@components/Blog/utils/html';
import type { components } from '@api-types/api-schema';

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

  // Превью строится по очищенному тексту: обрезка сырого HTML могла
  // разрезать тег и отдать карточке битую разметку
  const plainContent = stripHtml(article.content);

  /** Признак длинного контента (более 200 слов). */
  const isLong = plainContent.split(' ').length > 200;

  /** Усечённый текст для длинных статей (первые 50 слов). */
  const truncatedContent = isLong ? plainContent.split(' ').slice(0, 50).join(' ') : plainContent;

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow mb-4 rounded justify-content">
        <Card.Body>
          <h2 className="card-title fs-4">
            <a href={articleUrl}>{article.title}</a>
          </h2>
          <p className="card-text">{truncatedContent}</p>
          {isLong && <a href={articleUrl}>Читать дальше</a>}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ArticleCard;
