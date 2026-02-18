import React from 'react';
import { render, screen } from '@testing-library/react';
import PhotoTags from './PhotoTags';

/**
 * Тесты для компонента PhotoTags.
 * Проверяет корректность отображения тегов фотографии.
 */
describe('PhotoTags', () => {
  const mockTags = [
    { id: 1, name: 'Природа', slug: 'nature' },
    { id: 2, name: 'Пейзаж', slug: 'landscape' },
    { id: 3, name: 'Закат', slug: 'sunset' },
  ];

  /**
   * Проверяет, что компонент возвращает null, когда передан пустой массив тегов.
   */
  test('возвращает null если tags пустой массив', () => {
    const { container } = render(<PhotoTags tags={[]} />);
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент корректно отображает заголовок "Тэги:".
   */
  test('рендерит заголовок "Тэги:"', () => {
    render(<PhotoTags tags={mockTags} />);
    expect(screen.getByText('Тэги:')).toBeInTheDocument();
  });

  /**
   * Проверяет, что компонент корректно отображает все теги из массива.
   */
  test('рендерит все теги', () => {
    render(<PhotoTags tags={mockTags} />);
    expect(screen.getByText('Природа')).toBeInTheDocument();
    expect(screen.getByText('Пейзаж')).toBeInTheDocument();
    expect(screen.getByText('Закат')).toBeInTheDocument();
  });

  /**
   * Проверяет, что каждый тег имеет правильную ссылку на страницу тега.
   */
  test('каждый тег имеет правильную ссылку', () => {
    render(<PhotoTags tags={mockTags} />);
    const links = screen.getAllByRole('link');
    expect(links[0]).toHaveAttribute('href', '/gallery/tag/nature/');
    expect(links[1]).toHaveAttribute('href', '/gallery/tag/landscape/');
    expect(links[2]).toHaveAttribute('href', '/gallery/tag/sunset/');
  });

  /**
   * Проверяет, что ссылки на теги не имеют подчёркивания.
   */
  test('ссылки не имеют подчёркивания', () => {
    render(<PhotoTags tags={mockTags} />);
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveClass('text-decoration-none');
    });
  });

  /**
   * Проверяет, что компонент корректно отображается с одним тегом.
   */
  test('рендерит с одним тегом', () => {
    const singleTag = [{ id: 1, name: 'Тест', slug: 'test' }];
    render(<PhotoTags tags={singleTag} />);
    expect(screen.getByText('Тест')).toBeInTheDocument();
    expect(screen.getAllByRole('link')).toHaveLength(1);
  });

  /**
   * Проверяет, что компонент корректно отображается с множеством тегов.
   */
  test('рендерит с множеством тегов', () => {
    const manyTags = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      name: `Тег ${i + 1}`,
      slug: `tag-${i + 1}`,
    }));
    render(<PhotoTags tags={manyTags} />);
    manyTags.forEach(tag => {
      expect(screen.getByText(tag.name)).toBeInTheDocument();
    });
  });

  /**
   * Проверяет, что компонент корректно отображает теги со спецсимволами в названии.
   */
  test('рендерит со спецсимволами в названии тега', () => {
    const tagsWithSpecialChars = [
      { id: 1, name: 'Тег <>&"\'', slug: 'special' },
    ];
    render(<PhotoTags tags={tagsWithSpecialChars} />);
    expect(screen.getByText('Тег <>&"\'')).toBeInTheDocument();
  });

  /**
   * Проверяет, что теги отображаются в правильном порядке.
   */
  test('рендерит теги в правильном порядке', () => {
    const { container } = render(<PhotoTags tags={mockTags} />);
    const badges = container.querySelectorAll('.badge');
    expect(badges[0]).toHaveTextContent('Природа');
    expect(badges[1]).toHaveTextContent('Пейзаж');
    expect(badges[2]).toHaveTextContent('Закат');
  });
});
