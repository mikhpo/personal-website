import React from 'react';
import PropTypes from 'prop-types';
import { Card } from 'react-bootstrap';

/**
 * Компонент карточки статьи.
 *
 * Отображает превью статьи с заголовком и содержимым.
 * При длинном содержимом (более 200 слов) обрезает текст до 50 слов
 * и добавляет ссылку "Читать дальше".
 * Для администраторов дополняется ссылкой на страницу редактирования.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.article - Объект статьи
 * @param {number} props.article.id - ID статьи (первичный ключ)
 * @param {string} props.article.title - Заголовок статьи
 * @param {string} [props.article.content] - Полный текст статьи (HTML)
 * @param {string} [props.article.slug] - Слаг статьи
 * @param {string} [props.article.url] - Абсолютный URL статьи
 * @param {boolean} [props.isStaff=false] - Является ли текущий пользователь администратором
 * @return {JSX.Element} Компонент карточки статьи
 *
 * @example
 * // Использование компонента
 * const articleData = {
 *   id: 1,
 *   title: "Введение в React Hooks",
 *   content: "<p>Текст статьи...</p>",
 * };
 *
 * return <ArticleCard article={articleData} />;
 */
const ArticleCard = ({ article, isStaff = false }) => {
  const articleUrl = article.url || `/blog/${article.id}/`;
  const editUrl = article.url ? `${article.url}edit/` : `/blog/article/${article.slug}/edit/`;

  /**
   * Проверяет, является ли контент длинным (более 200 слов)
   * @type {boolean}
   */
  const isLong = article.content && article.content.split(' ').length > 200;

  /**
   * Усечённый HTML-контент для длинных статей (первые 50 слов)
   * @type {string}
   */
  const truncatedContent = isLong
    ? article.content.split(' ').slice(0, 50).join(' ')
    : article.content;

  return (
    <div className="container mb-3 pb-3">
      <Card className="shadow mb-4 rounded justify-content">
        <Card.Body>
          <h2 className="card-title fs-4">
            <a href={articleUrl}>{article.title}</a>
          </h2>
          {isStaff && (
            <a href={editUrl} className="d-inline-block mb-2 small">
              <i className="fas fa-edit me-1" />
              Редактировать
            </a>
          )}
          <p
            className="card-text"
            dangerouslySetInnerHTML={{ __html: truncatedContent }}
          />
          {isLong && (
            <a href={articleUrl}>Читать дальше</a>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

ArticleCard.propTypes = {
  article: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string,
    slug: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
  isStaff: PropTypes.bool,
};

ArticleCard.propTypes = {
  article: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string,
    slug: PropTypes.string,
    url: PropTypes.string,
    public: PropTypes.bool,
  }).isRequired,
  isStaff: PropTypes.bool,
};

export default ArticleCard;
