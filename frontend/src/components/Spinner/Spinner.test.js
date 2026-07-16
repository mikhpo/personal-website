import React from 'react';
import { render, screen } from '@testing-library/react';
import Spinner from './Spinner';

/**
 * Набор тестов для компонента индикатора загрузки Spinner.
 *
 * Проверяет корректность отображения спиннера с различными конфигурациями,
 * включая стандартные и пользовательские сообщения, CSS классы и доступность.
 */
describe('Spinner', () => {
  /**
   * Тест проверяет отображение спиннера с сообщением по умолчанию.
   *
   * Ожидается, что компонент отобразит текст "Загрузка..." в параграфе
   * и будет иметь роль status для обеспечения доступности.
   */
  test('рендерит со стандартным сообщением', () => {
    render(<Spinner />);
    expect(screen.getByText('Загрузка...', { selector: 'p' })).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение спиннера с пользовательским сообщением.
   *
   * Ожидается, что компонент отобразит переданное сообщение вместо стандартного
   * и не будет содержать текст "Загрузка...".
   */
  test('рендерит с пользовательским сообщением', () => {
    render(<Spinner message="Загрузка данных..." />);
    expect(screen.getByText('Загрузка данных...', { selector: 'p' })).toBeInTheDocument();
    expect(screen.queryByText('Загрузка...', { selector: 'p' })).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет, что спиннер использует анимацию border.
   *
   * Ожидается, что элемент спиннера имеет класс spinner-border,
   * который применяет соответствующую CSS анимацию.
   */
  test('spinner имеет animation="border"', () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector('.spinner-border');
    expect(spinner).toBeInTheDocument();
  });

  /**
   * Тест проверяет доступность сообщения через скрытый текст.
   *
   * Ожидается, что сообщение дублируется в элементе с классом visually-hidden
   * для обеспечения доступности для скринридеров.
   */
  test('отображает сообщение в visually-hidden для доступности', () => {
    render(<Spinner message="Тестовое сообщение" />);
    const hiddenText = screen.getByRole('status').querySelector('.visually-hidden');
    expect(hiddenText).toHaveTextContent('Тестовое сообщение');
  });

  /**
   * Тест проверяет отображение спиннера с пустым сообщением.
   *
   * Ожидается, что компонент корректно отображается даже при передаче
   * пустой строки в качестве сообщения.
   */
  test('рендерит с пустым сообщением', () => {
    render(<Spinner message="" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение спиннера с длинным сообщением.
   *
   * Ожидается, что компонент корректно отображает длинные текстовые сообщения
   * без обрезки или других проблем отображения.
   */
  test('рендерит с длинным сообщением', () => {
    const longMessage = 'Это очень длинное сообщение о загрузке данных из удалённого сервера';
    render(<Spinner message={longMessage} />);
    expect(screen.getByText(longMessage, { selector: 'p' })).toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение сообщения со специальными символами.
   *
   * Ожидается, что компонент корректно отображает сообщения, содержащие
   * специальные символы HTML без их интерпретации.
   */
  test('рендерит с сообщением содержащим спецсимволы', () => {
    const messageWithSpecialChars = 'Загрузка... <>&"\'';
    render(<Spinner message={messageWithSpecialChars} />);

    expect(screen.getByText(messageWithSpecialChars, { selector: 'p' })).toBeInTheDocument();
  });
});
