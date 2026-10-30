import React from 'react';
import { Card } from 'react-bootstrap';
import { countHtmlWords, truncateHtmlWords } from '@components/Blog/utils/html';
import type { components } from '@api-types/api-schema';

type Article = components['schemas']['Article'];

/** Свойства компонента карточки статьи. */
export interface ArticleCardProps {
  article: Article;
}

/**
 * Компонент карточки статьи.
 *
 * Отображает превью статьи с заголовком и содержимым в виде HTML: фотографии
 * и форматирование статьи видны прямо в карточке. При длинном содержимом
 * (более 200 слов) обрезает текст до 50 слов, не разрывая теги, и добавляет
 * ссылку "Читать дальше".
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

  // Порог длины считается по сырому HTML, как в прежнем серверном шаблоне:
  // словом считается любая группа символов между пробелами, включая атрибуты
  const isLong = countHtmlWords(article.content) > 200;

  // Обрезка не разрывает теги: закрывает открытые элементы и сохраняет
  // фотографии, встретившиеся до точки обрезки
  const preview = isLong ? truncateHtmlWords(article.content, 50) : article.content;

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow mb-4 rounded justify-content">
        <Card.Body>
          <h2 className="card-title fs-4">
            <a href={articleUrl}>{article.title}</a>
          </h2>
          <div className="card-text" dangerouslySetInnerHTML={{ __html: preview }} />
          {isLong && <a href={articleUrl}>Читать дальше</a>}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ArticleCard;
