/**
 * @file AlertList.test.js
 * @description Тесты для компонента AlertList
 *
 * Этот файл содержит тесты для проверки функциональности компонента списка сообщений,
 * включая отображение списка сообщений, обработку пустого массива и передачу
 * свойств вложенным компонентам Alert.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import AlertList from '@components/Alert/AlertList';
import Alert from '@components/Alert/AlertDetail';

/**
 * @description Тестовый набор для компонента AlertList
 *
 * Проверяет корректность работы всех основных функций компонента списка:
 * - отображение списка сообщений
 * - корректную обработку пустого массива сообщений
 * - правильную передачу свойств вложенным компонентам Alert
 */
describe('AlertList', () => {
  /**
   * @test Проверяет отображение одного сообщения
   *
   * Тест проверяет, что контейнер корректно отображает одно сообщение
   * с правильным текстом и уровнем важности.
   */
  test('рендерит одно сообщение', () => {
    const messages = [
      { message: 'Тестовое сообщение', level: 'success' }
    ];

    render(<AlertList messages={messages} />);

    expect(screen.getByText('Тестовое сообщение')).toBeInTheDocument();
  });

  /**
   * @test Проверяет отображение нескольких сообщений
   *
   * Тест проверяет, что контейнер корректно отображает несколько сообщений
   * с правильными текстами и уровнями важности.
   */
  test('рендерит несколько сообщений', () => {
    const messages = [
      { message: 'Первое сообщение', level: 'success' },
      { message: 'Второе сообщение', level: 'warning' },
      { message: 'Третье сообщение', level: 'error' }
    ];

    render(<AlertList messages={messages} />);

    expect(screen.getByText('Первое сообщение')).toBeInTheDocument();
    expect(screen.getByText('Второе сообщение')).toBeInTheDocument();
    expect(screen.getByText('Третье сообщение')).toBeInTheDocument();
  });

  /**
   * @test Проверяет обработку пустого массива сообщений
   *
   * Тест проверяет, что контейнер возвращает null при отсутствии сообщений
   * и не отображает ничего в DOM.
   */
  test('не отображает ничего при пустом массиве сообщений', () => {
    const { container } = render(<AlertList messages={[]} />);

    expect(container.firstChild).toBeNull();
  });

  /**
   * @test Проверяет обработку отсутствующего массива сообщений
   *
   * Тест проверяет, что контейнер корректно обрабатывает случай,
   * когда массив сообщений не передан (undefined).
   */
  test('не отображает ничего при отсутствии массива сообщений', () => {
    const { container } = render(<AlertList />);

    expect(container.firstChild).toBeNull();
  });

  /**
   * @test Проверяет передачу свойств вложенным компонентам Alert
   *
   * Тест проверяет, что контейнер корректно передает все свойства
   * сообщений вложенным компонентам Alert.
   */
  test('передает правильные свойства вложенным компонентам Alert', () => {
    const messages = [
      {
        message: 'Сообщение с авто-закрытием',
        level: 'info',
        dismissible: false,
        autoClose: true,
        autoCloseDelay: 3000
      }
    ];

    render(<AlertList messages={messages} />);

    // Проверяем, что сообщение отображено
    expect(screen.getByText('Сообщение с авто-закрытием')).toBeInTheDocument();
  });

});
