import React from 'react';
import PropTypes from 'prop-types';

/**
 * Компонент отдельного комментария к статье.
 *
 * Отображает комментарий с именем автора, датой публикации и текстом.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {Object} props.comment - Объект комментария
 * @param {number} props.comment.id - ID комментария
 * @param {string} props.comment.author_username - Имя автора комментария
 * @param {string} props.comment.content - Текст комментария (HTML)
 * @param {string} props.comment.posted - Дата публикации
 * @return {JSX.Element} Компонент комментария
 *
 * @example
 * // Использование компонента
 * const commentData = {
 *   id: 1,
 *   author_username: "user123",
 *   content: "Отличная статья!",
 *   posted: "15 янв. 2024 г., 10:00:00"
 * };
 *
 * return <Comment comment={commentData} />;
 */
const Comment = ({ comment }) => {
  return (
    <li>
      <div>
        <span>
          <strong className="fw-bolder">{comment.author_username}</strong>
          <span className="mx-2">&middot;</span>
          <small className="text-muted">{comment.posted}</small>
        </span>
        <p dangerouslySetInnerHTML={{ __html: comment.content }} />
      </div>
    </li>
  );
};

Comment.propTypes = {
  comment: PropTypes.shape({
    id: PropTypes.number.isRequired,
    author_username: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    posted: PropTypes.string.isRequired,
  }).isRequired,
};

export default Comment;
