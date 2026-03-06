/**
 * Тесты для компонента CommentList.
 *
 * Проверяет корректность отображения списка комментариев с различными наборами данных,
 * включая обработку пустого списка, передачу данных в дочерние компоненты.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import CommentList from './CommentList';

// Мок для компонента Comment
jest.mock('@components/Blog/Comment/Comment', () => {
  return function MockComment({ comment }) {
    return (
      <li data-testid="comment">
        <span data-testid="comment-author">{comment.author_username}</span>
      </li>
    );
  };
});

describe('CommentList', () => {
  const mockComments = [
    { id: 1, author_username: 'user1', content: 'Отлично!', posted: '15 янв. 2024 г.' },
    { id: 2, author_username: 'user2', content: 'Согласен', posted: '15 янв. 2024 г.' },
    { id: 3, author_username: 'user3', content: 'Полезно', posted: '16 янв. 2024 г.' },
  ];

  /**
   * Проверяет, что компонент корректно отображает список комментариев.
   * Каждый комментарий должен быть представлен в списке.
   */
  test('отображает список комментариев', () => {
    render(<CommentList comments={mockComments} />);
    const comments = screen.getAllByTestId('comment');
    expect(comments).toHaveLength(3);
  });

  /**
   * Проверяет, что данные комментариев корректно передаются в дочерний компонент Comment.
   * Имена авторов должны отображаться правильно.
   */
  test('передаёт правильные props в Comment', () => {
    render(<CommentList comments={mockComments} />);
    const authors = screen.getAllByTestId('comment-author');
    expect(authors[0]).toHaveTextContent('user1');
    expect(authors[1]).toHaveTextContent('user2');
    expect(authors[2]).toHaveTextContent('user3');
  });

  /**
   * Проверяет, что компонент возвращает null при пустом массиве комментариев.
   * Пустой список не должен рендериться.
   */
  test('возвращает null при пустом массиве комментариев', () => {
    const { container } = render(<CommentList comments={[]} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null при undefined.
   * Отсутствие данных не должно вызывать ошибок рендеринга.
   */
  test('возвращает null при undefined', () => {
    const { container } = render(<CommentList comments={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null при null.
   * Null значение не должно вызывать ошибок рендеринга.
   */
  test('возвращает null при null', () => {
    const { container } = render(<CommentList comments={null} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет корректность отображения списка с одним комментарием.
   * Компонент должен обрабатывать единичные элементы.
   */
  test('обрабатывает один комментарий', () => {
    const singleComment = [mockComments[0]];
    render(<CommentList comments={singleComment} />);
    expect(screen.getAllByTestId('comment')).toHaveLength(1);
  });

  /**
   * Проверяет корректность отображения большого количества комментариев.
   * Компонент должен справляться с длинными списками.
   */
  test('обрабатывает большое количество комментариев', () => {
    const manyComments = Array(50).fill(null).map((_, i) => ({
      id: i + 1,
      author_username: `user${i + 1}`,
      content: `Комментарий ${i + 1}`,
      posted: '15 янв. 2024 г.',
    }));
    render(<CommentList comments={manyComments} />);
    expect(screen.getAllByTestId('comment')).toHaveLength(50);
  });

  /**
   * Проверяет корректность отображения комментариев с одинаковыми авторами.
   * Компонент должен правильно обрабатывать повторяющиеся имена.
   */
  test('обрабатывает комментарии с одинаковыми авторами', () => {
    const commentsWithSameAuthor = [
      { id: 1, author_username: 'user1', content: 'Первый', posted: '15 янв. 2024 г.' },
      { id: 2, author_username: 'user1', content: 'Второй', posted: '16 янв. 2024 г.' },
    ];
    render(<CommentList comments={commentsWithSameAuthor} />);
    expect(screen.getAllByTestId('comment')).toHaveLength(2);
  });
});
