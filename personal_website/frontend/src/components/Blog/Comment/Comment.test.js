/**
 * Тесты для компонента Comment.
 *
 * Проверяет корректность отображения комментария с различными наборами данных,
 * включая имя автора, дату публикации, текст комментария и HTML-контент.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import Comment from './Comment';

describe('Comment', () => {
  const mockComment = {
    id: 1,
    author_username: 'user123',
    content: 'Отличный комментарий!',
    posted: '15 янв. 2024 г., 10:00:00',
  };

  /**
   * Проверяет, что компонент корректно отображает имя автора комментария.
   * Имя автора должно быть в элементе с классом fw-bolder.
   */
  test('отображает имя автора', () => {
    render(<Comment comment={mockComment} />);
    expect(screen.getByText('user123')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно отображает дату публикации.
   * Дата должна быть в элементе с классом text-muted.
   */
  test('отображает дату публикации', () => {
    render(<Comment comment={mockComment} />);
    expect(screen.getByText('15 янв. 2024 г., 10:00:00')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно отображает текст комментария.
   * Текст комментария должен отображаться в элементе p.
   */
  test('отображает текст комментария', () => {
    render(<Comment comment={mockComment} />);
    expect(screen.getByText('Отличный комментарий!')).toBeInTheDocument();
  });

  /**
   * Проверяет, что HTML-контент комментария корректно рендерится.
   * HTML-теги в контенте должны обрабатываться через dangerouslySetInnerHTML.
   */
  test('рендерит HTML контент', () => {
    const commentWithHtml = {
      ...mockComment,
      content: '<p>Текст с <strong>HTML</strong> тегами</p>',
    };
    render(<Comment comment={commentWithHtml} />);
    expect(screen.getByText('HTML')).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения комментария с пустым текстом.
   * Компонент должен корректно обрабатывать пустую строку в поле content.
   */
  test('рендерит с пустым текстом', () => {
    const commentWithEmptyContent = {
      ...mockComment,
      content: '',
    };
    const { container } = render(<Comment comment={commentWithEmptyContent} />);
    const paragraphElement = container.querySelector('p');
    expect(paragraphElement).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения специальных символов в тексте.
   * Компонент должен корректно экранировать и отображать специальные символы.
   */
  test('рендерит со спецсимволами в тексте', () => {
    const commentWithSpecialChars = {
      ...mockComment,
      content: 'Текст с <символами> & "спецсимволами"',
    };
    render(<Comment comment={commentWithSpecialChars} />);
    expect(screen.getByText('Текст с <символами> & "спецсимволами"')).toBeInTheDocument();
  });

  /**
   * Проверяет корректность отображения комментария с длинной датой.
   * Компонент должен корректно отображать даты произвольной длины.
   */
  test('рендерит с длинной датой', () => {
    const longDate = 'д'.repeat(100);
    const commentWithLongDate = {
      ...mockComment,
      posted: longDate,
    };
    render(<Comment comment={commentWithLongDate} />);
    expect(screen.getByText(longDate)).toBeInTheDocument();
  });
});
