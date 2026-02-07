/**
 * @file Alert.test.js
 * @description Тесты для компонента Alert
 *
 * Этот файл содержит тесты для проверки функциональности компонента Alert,
 * включая отображение сообщений, ручное и автоматическое закрытие.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Alert from './Alert';

/**
 * @description Тестовый набор для компонента Alert
 *
 * Проверяет корректность работы всех основных функций компонента:
 * - отображение сообщения
 * - ручное закрытие через кнопку
 * - автоматическое закрытие через заданное время
 */
describe('Alert', () => {
  /**
   * @test Проверяет отображение сообщения
   *
   * Тест проверяет, что компонент корректно отображает переданное ему сообщение
   * с правильным уровнем важности.
   */
  test('рендерит сообщение', () => {
    render(<Alert message="Тест" level="success" />);
    expect(screen.getByText('Тест')).toBeInTheDocument();
  });

  /**
   * @test Проверяет ручное закрытие сообщения
   *
   * Тест проверяет, что сообщение корректно скрывается при клике
   * на кнопку закрытия, когда включена опция dismissible.
   */
  test('закрывается при клике на кнопку закрытия', async () => {
    const user = userEvent.setup();
    render(<Alert message="Тест" level="success" dismissible />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Тест')).not.toBeInTheDocument();
    });
  });

  /**
   * @test Проверяет автоматическое закрытие сообщения
   *
   * Тест проверяет, что сообщение автоматически скрывается через
   * заданное время, когда включена опция autoClose.
   */
  test('автоматически закрывается через заданное время', async () => {
    // Устанавливаем задержку авто закрытия в 100 мс для теста
    render(<Alert message="Тест" level="success" autoClose autoCloseDelay={100} />);

    expect(screen.getByText('Тест')).toBeInTheDocument();

    // Ждем 200 мс - этого времени достаточно для закрытия сообщения (в 2 раза больше задержки)
    await waitFor(
      () => {
        expect(screen.queryByText('Тест')).not.toBeInTheDocument();
      },
      { timeout: 200 }
    );
  });

  /**
   * @test Проверяет рендеринг HTML в сообщении
   *
   * Тест проверяет, что компонент корректно рендерит HTML-разметку
   * в тексте сообщения (например, ссылки и жирный текст).
   */
  test('рендерит HTML в сообщении', () => {
    const htmlMessage = 'Загружено <b>5</b> фотографий в альбом <a href="/gallery/albums/test/" class="alert-link">Тестовый альбом</a>';
    const { container } = render(<Alert message={htmlMessage} level="success" />);

    // Проверяем наличие жирного текста
    const boldElement = container.querySelector('b');
    expect(boldElement).toBeInTheDocument();
    expect(boldElement).toHaveTextContent('5');

    // Проверяем наличие ссылки
    const linkElement = container.querySelector('a.alert-link');
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveTextContent('Тестовый альбом');
    expect(linkElement).toHaveAttribute('href', '/gallery/albums/test/');
  });
});
