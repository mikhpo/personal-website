import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TagButton from './TagButton';

/**
 * Набор тестов для компонента TagButton.
 * Проверяет рендеринг тега, формирование ссылки, CSS-классы и обработку кликов.
 */
describe('TagButton', () => {
  const mockTag = {
    id: 1,
    name: 'Природа',
    slug: 'nature',
  };

  /**
   * Проверяет, что компонент отображает название тега.
   * Ожидается, что текст тега будет виден на странице.
   */
  test('рендерит название тега', () => {
    render(<TagButton tag={mockTag} />);
    expect(screen.getByText('Природа')).toBeInTheDocument();
  });

  /**
   * Проверяет, что ссылка кнопки сформирована правильно.
   * Ожидается, что href будет содержать слаг тега в формате /gallery/tag/{slug}/.
   */
  test('кнопка имеет правильную ссылку', () => {
    render(<TagButton tag={mockTag} />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('href', '/gallery/tag/nature/');
  });

  /**
   * Проверяет наличие CSS-класса варианта кнопки.
   * Ожидается, что кнопка будет иметь класс btn-outline-dark.
   */
  test('кнопка имеет вариант "outline-dark"', () => {
    render(<TagButton tag={mockTag} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-outline-dark');
  });

  /**
   * Проверяет наличие CSS-класса полной ширины.
   * Ожидается, что кнопка будет иметь класс w-100.
   */
  test('кнопка имеет класс полной ширины', () => {
    render(<TagButton tag={mockTag} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('w-100');
  });

  /**
   * Проверяет отсутствие ошибок при клике без обработчика onClick.
   * Ожидается, что клик по кнопке не вызовет ошибок, если onClick не передан.
   */
  test('не вызывает onClick если не передан', () => {
    render(<TagButton tag={mockTag} />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    // Не должно быть ошибок
  });

  /**
   * Проверяет вызов обработчика onClick с объектом тега при клике.
   * Ожидается, что onClick будет вызван один раз с объектом тега.
   */
  test('вызывает onClick с тегом при клике', () => {
    const handleClick = jest.fn();
    render(<TagButton tag={mockTag} onClick={handleClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(handleClick).toHaveBeenCalledWith(mockTag);
  });

  /**
   * Проверяет множественные вызовы обработчика onClick.
   * Ожидается, что onClick будет вызываться при каждом клике.
   */
  test('вызывает onClick несколько раз при множественных кликах', () => {
    const handleClick = jest.fn();
    render(<TagButton tag={mockTag} onClick={handleClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);
    fireEvent.click(button);
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(3);
  });

  /**
   * Проверяет рендеринг компонента с различными тегами.
   * Ожидается, что каждый тег отобразится с правильным названием и ссылкой.
   */
  test('рендерит с различными тегами', () => {
    const tags = [
      { id: 1, name: 'Пейзаж', slug: 'landscape' },
      { id: 2, name: 'Портрет', slug: 'portrait' },
      { id: 3, name: 'Архитектура', slug: 'architecture' },
    ];

    tags.forEach(tag => {
      const { unmount } = render(<TagButton tag={tag} />);
      expect(screen.getByText(tag.name)).toBeInTheDocument();
      expect(screen.getByRole('button')).toHaveAttribute('href', `/gallery/tag/${tag.slug}/`);
      unmount();
    });
  });

  /**
   * Проверяет отображение длинного названия тега.
   * Ожидается, что длинный текст тега корректно отобразится.
   */
  test('рендерит с длинным названием тега', () => {
    const longTag = {
      id: 1,
      name: 'Очень длинное название тега которое может занимать много места',
      slug: 'long-tag',
    };
    render(<TagButton tag={longTag} />);

    expect(screen.getByText(longTag.name)).toBeInTheDocument();
  });

  /**
   * Проверяет отображение специальных символов в названии тега.
   * Ожидается, что спецсимволы <>&"' корректно отобразятся.
   */
  test('рендерит со спецсимволами в названии', () => {
    const tagWithSpecialChars = {
      id: 1,
      name: 'Тег <>&"\'',
      slug: 'special',
    };
    render(<TagButton tag={tagWithSpecialChars} />);

    expect(screen.getByText(tagWithSpecialChars.name)).toBeInTheDocument();
  });

  /**
   * Проверяет формирование ссылки со сложным slug.
   * Ожидается, что slug с цифрами и дефисами корректно включится в href.
   */
  test('рендерит с slug содержащим цифры и дефисы', () => {
    const tagWithComplexSlug = {
      id: 1,
      name: 'Тест',
      slug: 'test-123-tag-456',
    };
    render(<TagButton tag={tagWithComplexSlug} />);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('href', '/gallery/tag/test-123-tag-456/');
  });

  /**
   * Проверяет, что элемент кнопки является ссылкой.
   * Ожидается, что элемент будет иметь role="button".
   */
  test('кнопка является ссылкой', () => {
    render(<TagButton tag={mockTag} />);

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  /**
   * Проверяет передачу правильного объекта тега в обработчик onClick.
   * Ожидается, что onClick получит точный объект тега при клике.
   */
  test('передаёт правильный объект тега в onClick', () => {
    const handleClick = jest.fn();
    const customTag = {
      id: 99,
      name: 'Кастомный тег',
      slug: 'custom',
    };
    render(<TagButton tag={customTag} onClick={handleClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledWith(customTag);
  });

  /**
   * Проверяет сохранение функциональности ссылки при наличии обработчика onClick.
   * Ожидается, что кнопка сохранит href и вызовет onClick одновременно.
   */
  test('сохраняет функциональность ссылки при onClick', () => {
    const handleClick = jest.fn();
    render(<TagButton tag={mockTag} onClick={handleClick} />);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('href', '/gallery/tag/nature/');

    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalled();
  });
});
