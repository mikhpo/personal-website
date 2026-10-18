import React from 'react';
import Comment from '@components/Blog/Comment/Comment';
import type { components } from '../../../types/api-schema';

type CommentData = components['schemas']['Comment'];

/** Свойства компонента списка комментариев. */
export interface CommentListProps {
  /** Массив комментариев; при отсутствии или пустоте не рендерит ничего. */
  comments?: CommentData[];
}

/**
 * Компонент списка комментариев к статье.
 *
 * @example
 * <CommentList
 *   comments={[
 *     { id: 1, author_username: 'user1', content: 'Отлично!', posted: '15 янв. 2024 г.' },
 *     { id: 2, author_username: 'user2', content: 'Согласен', posted: '15 янв. 2024 г.' },
 *   ]}
 * />
 */
const CommentList = ({ comments }: CommentListProps) => {
  if (!comments || comments.length === 0) {
    return null;
  }

  return (
    <ul>
      {comments.map((comment) => (
        <Comment key={comment.id} comment={comment} />
      ))}
    </ul>
  );
};

export default CommentList;
