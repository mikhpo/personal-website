/**
 * Тесты для компонента ThemeToggle.
 *
 * Проверяют кнопку переключения темы, состав и состояние выпадающего меню,
 * сохранение выбора в localStorage и атрибут data-bs-theme на <html>.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeToggle from './ThemeToggle';

/**
 * Создает управляемый стаб window.matchMedia.
 * @param {boolean} matchesDark - Совпадает ли запрос prefers-color-scheme: dark
 * @return {Function} Функция matchMedia
 */
const stubMatchMedia = (matchesDark) => {
  const listeners = new Set();
  const mediaQuery = {
    matches: matchesDark,
    addEventListener: jest.fn((event, listener) => listeners.add(listener)),
    removeEventListener: jest.fn(),
  };
  return jest.fn(() => mediaQuery);
};

/**
 * Открывает выпадающее меню выбора темы кликом по кнопке.
 */
const openMenu = () => {
  fireEvent.click(screen.getByRole('button', { name: 'Выбор темы' }));
};

describe('ThemeToggle', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute('data-bs-theme');
    window.matchMedia = stubMatchMedia(false);
  });

  /**
   * Проверяет кнопку переключения темы.
   */
  describe('кнопка', () => {
    test('рендерится с доступным названием', () => {
      render(<ThemeToggle />);

      expect(screen.getByRole('button', { name: 'Выбор темы' })).toBeInTheDocument();
    });

    test('в системном режиме показывает иконку автоматического режима', () => {
      render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: 'Выбор темы' });
      expect(button.querySelector('i')).toHaveClass('bi-circle-half');
    });

    test('при явной темной теме показывает иконку луны', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: 'Выбор темы' });
      expect(button.querySelector('i')).toHaveClass('bi-moon-stars-fill');
    });

    test('при явной светлой теме показывает иконку солнца', () => {
      window.localStorage.setItem('theme', JSON.stringify('light'));

      render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: 'Выбор темы' });
      expect(button.querySelector('i')).toHaveClass('bi-sun-fill');
    });
  });

  /**
   * Проверяет содержимое выпадающего меню.
   */
  describe('меню выбора', () => {
    test('содержит три варианта темы', () => {
      render(<ThemeToggle />);
      openMenu();

      expect(screen.getByText('Светлая')).toBeInTheDocument();
      expect(screen.getByText('Тёмная')).toBeInTheDocument();
      expect(screen.getByText('Системная')).toBeInTheDocument();
    });

    test('отмечает активной системную тему без явного выбора', () => {
      render(<ThemeToggle />);
      openMenu();

      expect(screen.getByText('Системная')).toHaveClass('active');
      expect(screen.getByText('Светлая')).not.toHaveClass('active');
      expect(screen.getByText('Тёмная')).not.toHaveClass('active');
    });

    test('отмечает активной явно выбранную тему', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      render(<ThemeToggle />);
      openMenu();

      expect(screen.getByText('Тёмная')).toHaveClass('active');
      expect(screen.getByText('Системная')).not.toHaveClass('active');
    });
  });

  /**
   * Проверяет сохранение выбранной темы.
   */
  describe('выбор темы', () => {
    test('выбор "Тёмная" сохраняет тему и обновляет атрибут на <html>', () => {
      render(<ThemeToggle />);
      openMenu();

      fireEvent.click(screen.getByText('Тёмная'));

      expect(window.localStorage.getItem('theme')).toBe(JSON.stringify('dark'));
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
      expect(screen.getByRole('button', { name: 'Выбор темы' }).querySelector('i')).toHaveClass('bi-moon-stars-fill');
    });

    test('выбор "Светлая" сохраняет тему и обновляет атрибут на <html>', () => {
      render(<ThemeToggle />);
      openMenu();

      fireEvent.click(screen.getByText('Светлая'));

      expect(window.localStorage.getItem('theme')).toBe(JSON.stringify('light'));
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'light');
    });

    test('выбор "Системная" удаляет явный выбор и следует системной теме', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));
      window.matchMedia = stubMatchMedia(false);

      render(<ThemeToggle />);
      openMenu();

      fireEvent.click(screen.getByText('Системная'));

      expect(window.localStorage.getItem('theme')).toBeNull();
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'light');
      expect(screen.getByRole('button', { name: 'Выбор темы' }).querySelector('i')).toHaveClass('bi-circle-half');
    });
  });
});
