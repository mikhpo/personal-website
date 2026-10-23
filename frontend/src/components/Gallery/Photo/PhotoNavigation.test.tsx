/**
 * Тесты для компонента PhotoNavigation.
 *
 * Проверяют рендер стрелок перехода к соседним фотографиям альбома
 * и размещение дочерних действий между ними.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import PhotoNavigation from './PhotoNavigation';

describe('PhotoNavigation', () => {
  const previousUrl = '/gallery/photo/1/';
  const nextUrl = '/gallery/photo/3/';

  test('рендерит обе стрелки с корректными href', () => {
    render(<PhotoNavigation previousUrl={previousUrl} nextUrl={nextUrl} />);

    const prevLink = screen.getByText('<');
    expect(prevLink).toHaveAttribute('href', previousUrl);
    expect(prevLink).toHaveAttribute('id', 'previous-photo-link');

    const nextLink = screen.getByText('>');
    expect(nextLink).toHaveAttribute('href', nextUrl);
    expect(nextLink).toHaveAttribute('id', 'next-photo-link');
  });

  test('не рендерит стрелки без URL', () => {
    const { container } = render(<PhotoNavigation previousUrl={null} nextUrl={null} />);

    expect(screen.queryByText('<')).not.toBeInTheDocument();
    expect(screen.queryByText('>')).not.toBeInTheDocument();
    expect(container).toBeEmptyDOMElement();
  });

  test('рендерит только предыдущую стрелку', () => {
    render(<PhotoNavigation previousUrl={previousUrl} nextUrl={null} />);

    expect(screen.getByText('<')).toBeInTheDocument();
    expect(screen.queryByText('>')).not.toBeInTheDocument();
  });

  test('рендерит только следующую стрелку', () => {
    render(<PhotoNavigation previousUrl={null} nextUrl={nextUrl} />);

    expect(screen.queryByText('<')).not.toBeInTheDocument();
    expect(screen.getByText('>')).toBeInTheDocument();
  });

  test('размещает дочерние действия между стрелками', () => {
    const { container } = render(
      <PhotoNavigation previousUrl={previousUrl} nextUrl={nextUrl}>
        <button type="button">О фото</button>
      </PhotoNavigation>,
    );

    const children = container.children;
    expect(children[0]).toHaveAttribute('id', 'previous-photo-link');
    expect(screen.getByText('О фото')).toBeInTheDocument();
    expect(children[children.length - 1]).toHaveAttribute('id', 'next-photo-link');
  });
});
