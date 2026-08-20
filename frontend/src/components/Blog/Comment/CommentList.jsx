import React from 'react';
import PropTypes from 'prop-types';
import Comment from '@components/Blog/Comment/Comment';

/**
 * Компонент списка комментариев к статье.
 *
 * Отображает список комментариев. При отсутствии комментариев - ничего не рендерит.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {Array} [props.comments] - Массив комментариев
 * @return {JSX.Element|null} Компонент списка комментариев или null
 *
 * @example
 * // Использование компонента
 * const commentsData = [
 *   { id: 1, author_username: "user1", content: "Отлично!", posted: "15 янв. 2024 г." },
 *   { id: 2, author_username: "user2", content: "Согласен", posted: "15 янв. 2024 г." }
 * ];
 *
 * return <CommentList comments={commentsData} />;
 */
const CommentList = ({ comments }) => {
  if (!comments || comments.length === 0) {
    return null;
  }

  return (
    <ul>
      {comments.map(comment => (
        <Comment
          key={comment.id}
          comment={comment}
        />
      ))}
    </ul>
  );
};

CommentList.propTypes = {
  comments: PropTypes.arrayOf(PropTypes.object),
};

export default CommentList;
