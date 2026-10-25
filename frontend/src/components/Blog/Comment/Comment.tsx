import React from 'react';
import type { components } from '@api-types/api-schema';

type CommentData = components['schemas']['Comment'];

/** Свойства компонента отдельного комментария. */
export interface CommentProps {
  comment: CommentData;
}

/**
 * Компонент отдельного комментария к статье.
 *
 * Отображает комментарий с именем автора, датой публикации и текстом.
 *
 * @example
 * <Comment
 *   comment={{
 *     id: 1,
 *     author_username: 'user123',
 *     content: 'Отличная статья!',
 *     posted: '15 янв. 2024 г., 10:00:00',
 *   }}
 * />
 */
const Comment = ({ comment }: CommentProps) => {
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

export default Comment;
