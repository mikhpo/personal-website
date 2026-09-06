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
import Alert from '@components/Alert/AlertDetail';

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

  /**
   * @test Проверяет отображение дополнительных действий (actions)
   *
   * Тест проверяет, что компонент корректно отображает дополнительные действия
   * в отдельном блоке под основным сообщением.
   */
  test('рендерит дополнительные действия', () => {
    const actions = (
      <button className="btn btn-primary" onClick={() => {}}>
        Повторить
      </button>
    );

    const { container } = render(
      <Alert
        message="Ошибка загрузки данных"
        level="error"
        actions={actions}
      />
    );

    // Проверяем, что основное сообщение отображено
    expect(screen.getByText('Ошибка загрузки данных')).toBeInTheDocument();

    // Проверяем, что дополнительные действия отображены
    const actionButton = container.querySelector('.btn.btn-primary');
    expect(actionButton).toBeInTheDocument();
    expect(actionButton).toHaveTextContent('Повторить');

    // Проверяем, что действия находятся в блоке с отступом
    const actionsContainer = container.querySelector('.mt-2');
    expect(actionsContainer).toBeInTheDocument();
    expect(actionsContainer).toContainElement(actionButton);
  });

  /**
   * @test Проверяет, что дополнительные действия не отображаются, если не переданы
   *
   * Тест проверяет, что при отсутствии параметра actions не создается
   * дополнительный блок для действий.
   */
  test('не отображает блок действий, если actions не передан', () => {
    const { container } = render(
      <Alert message="Тестовое сообщение" level="info" />
    );

    // Проверяем, что сообщение отображено
    expect(screen.getByText('Тестовое сообщение')).toBeInTheDocument();

    // Проверяем, что блок действий отсутствует
    const actionsContainer = container.querySelector('.mt-2');
    expect(actionsContainer).not.toBeInTheDocument();
  });

  /**
   * @test Проверяет отображение различных типов дополнительных действий
   *
   * Тест проверяет, что компонент может отображать различные типы
   * React-элементов в качестве дополнительных действий.
   */
  test('рендерит различные типы дополнительных действий', () => {
    const actions = (
      <div>
        <button className="btn btn-primary me-2">Действие 1</button>
        <a href="/actions/" className="btn btn-secondary">Действие 2</a>
      </div>
    );

    const { container } = render(
      <Alert
        message="Сообщение с несколькими действиями"
        level="warning"
        actions={actions}
      />
    );

    // Проверяем основное сообщение
    expect(screen.getByText('Сообщение с несколькими действиями')).toBeInTheDocument();

    // Проверяем первое действие (кнопка)
    const actionButton1 = container.querySelector('.btn.btn-primary');
    expect(actionButton1).toBeInTheDocument();
    expect(actionButton1).toHaveTextContent('Действие 1');

    // Проверяем второе действие (ссылка)
    const actionButton2 = container.querySelector('.btn.btn-secondary');
    expect(actionButton2).toBeInTheDocument();
    expect(actionButton2).toHaveTextContent('Действие 2');

    // Проверяем, что оба действия находятся в блоке с отступом
    const actionsContainer = container.querySelector('.mt-2');
    expect(actionsContainer).toBeInTheDocument();
    expect(actionsContainer).toContainElement(actionButton1);
    expect(actionsContainer).toContainElement(actionButton2);
  });
});
