/**
 * Тесты для компонента BaseCard.
 *
 * Проверяют корректность отображения базовой карточки с различными наборами данных,
 * включая варианты отображения (centered/left), обработку отсутствия изображения,
 * правильность ссылок и дополнительные пропсы.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import BaseCard from './BaseCard';

describe('BaseCard', () => {
  const defaultProps = {
    title: 'Тестовая карточка',
    url: '/test/page/',
  };

  /**
   * Проверяет базовый рендер без изображения.
   */
  describe('базовый рендер', () => {
    test('рендерит с минимальными props', () => {
      render(<BaseCard {...defaultProps} />);
      expect(screen.getByText('Тестовая карточка')).toBeInTheDocument();
    });

    test('рендерит с описанием', () => {
      render(<BaseCard {...defaultProps} description="Тестовое описание" />);
      expect(screen.getByText('Тестовое описание')).toBeInTheDocument();
    });

    test('не отображает описание когда его нет', () => {
      const { container } = render(<BaseCard {...defaultProps} />);
      const cardText = container.querySelector('.card-text');
      expect(cardText).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет рендер с изображением.
   */
  describe('рендер с изображением', () => {
    const propsWithImage = {
      ...defaultProps,
      image: '/media/test/image.jpg',
    };

    test('рендерит изображение', () => {
      render(<BaseCard {...propsWithImage} />);
      const img = screen.getByRole('img');
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute('src', '/media/test/image.jpg');
    });

    test('использует title как fallback для alt текста', () => {
      render(<BaseCard {...propsWithImage} />);
      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('alt', 'Тестовая карточка');
    });

    test('использует imageAlt когда указан', () => {
      render(<BaseCard {...propsWithImage} imageAlt="Альтернативный текст" />);
      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('alt', 'Альтернативный текст');
    });

    test('image является ссылкой на страницу', () => {
      render(<BaseCard {...propsWithImage} />);
      const img = screen.getByRole('img');
      const link = img.closest('a');
      expect(link).toHaveAttribute('href', '/test/page/');
    });
  });

  /**
   * Проверяет ссылки.
   */
  describe('ссылки', () => {
    test('заголовок является ссылкой', () => {
      render(<BaseCard {...defaultProps} />);
      const link = screen.getByRole('link', { name: 'Тестовая карточка' });
      expect(link).toHaveAttribute('href', '/test/page/');
    });

    test('все ссылки ведут на один URL', () => {
      const propsWithImage = {
        ...defaultProps,
        image: '/media/test/image.jpg',
      };
      render(<BaseCard {...propsWithImage} />);
      const links = screen.getAllByRole('link');
      links.forEach((link) => {
        expect(link).toHaveAttribute('href', '/test/page/');
      });
    });
  });

  /**
   * Проверяет отсутствие изображения.
   */
  describe('отсутствие изображения', () => {
    test('не отображает изображение когда image не передан', () => {
      render(<BaseCard {...defaultProps} />);
      expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });

    test('не отображает изображение когда image пустая строка', () => {
      render(<BaseCard {...defaultProps} image="" />);
      expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });

    test('не отображает изображение когда image undefined', () => {
      render(<BaseCard {...defaultProps} image={undefined} />);
      expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет дополнительные пропсы.
   */
  describe('дополнительные пропсы', () => {
    test('применяет дополнительные className', () => {
      const { container } = render(<BaseCard {...defaultProps} className="custom-class" />);
      const card = container.querySelector('.card');
      expect(card).toHaveClass('custom-class');
    });

    test('сохраняет базовые классы при добавлении className', () => {
      const { container } = render(<BaseCard {...defaultProps} className="custom-class" />);
      const card = container.querySelector('.card');
      expect(card).toHaveClass('shadow');
      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('rounded');
      expect(card).toHaveClass('h-100');
    });

    test('пробрасывает cardImgProps в Card.Img', () => {
      const propsWithImage = {
        ...defaultProps,
        image: '/media/test/image.jpg',
        cardImgProps: { className: 'custom-img-class' },
      };
      const { container } = render(<BaseCard {...propsWithImage} />);
      const img = container.querySelector('.card-img-top');
      expect(img).toHaveClass('custom-img-class');
    });

    test('поддерживает loading="lazy" для изображения по умолчанию', () => {
      const propsWithImage = {
        ...defaultProps,
        image: '/media/test/image.jpg',
      };
      const { container } = render(<BaseCard {...propsWithImage} />);
      const img = container.querySelector('.card-img-top');
      expect(img).toHaveAttribute('loading', 'lazy');
    });
  });

  /**
   * Проверяет обработку специальных символов.
   */
  describe('специальные символы', () => {
    test('корректно отображает спецсимволы в заголовке', () => {
      const props = {
        ...defaultProps,
        title: 'Карточка <>&"\'',
      };
      render(<BaseCard {...props} />);
      expect(screen.getByText('Карточка <>&"\'')).toBeInTheDocument();
    });

    test('корректно отображает спецсимволы в описании', () => {
      const props = {
        ...defaultProps,
        description: 'Описание с <>&"\' символами',
      };
      render(<BaseCard {...props} />);
      expect(screen.getByText('Описание с <>&"\' символами')).toBeInTheDocument();
    });
  });
});
