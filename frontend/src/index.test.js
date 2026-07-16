/**
 * @file Тесты для функции mountReactComponent из index.js
 *
 * Этот файл содержит тесты для основной функции монтирования React компонентов,
 * которая используется для интеграции React компонентов в Django шаблоны.
 */

// Импорт тестируемой функции
import './index.js';

// Замена react-dom/client на мок для изоляции тестов от реального DOM
jest.mock('react-dom/client', () => {
  const mockRender = jest.fn();
  const mockCreateRoot = jest.fn(() => ({
    render: mockRender,
  }));
  return { createRoot: mockCreateRoot };
});

/**
 * Набор тестов для функции mountReactComponent
 * @module index.test
 */
describe('mountReactComponent', () => {
  let mockElement;

  /**
   * Подготовка тестового окружения перед каждым тестом:
   * - Создание тестового DOM элемента
   * - Добавление элемента в document.body
   * - Очистка всех моков
   */
  beforeEach(() => {
    // Создание тестового DOM элемента с ID 'test-container'
    mockElement = document.createElement('div');
    mockElement.id = 'test-container';
    document.body.appendChild(mockElement);

    // Очистка всех моков перед каждым тестом
    jest.clearAllMocks();
  });

  /**
   * Очистка тестового окружения после каждого теста:
   * - Удаление тестового элемента из document.body
   */
  afterEach(() => {
    document.body.removeChild(mockElement);
  });

  /**
   * Тест успешного монтирования компонента
   * Проверяет, что функция правильно вызывает createRoot и рендерит компонент
   */
  test('должен успешно монтировать компонент при наличии элемента', async () => {
    // Настройка мока для динамического импорта компонента
    jest.mock('./components/TestComponent', () => ({
      __esModule: true,
      default: () => 'Mocked Component',
    }), { virtual: true });

    // Вызов тестируемой функции
    window.mountReactComponent('TestComponent', 'test-container', { testProp: 'test' });

    // Ожидание разрешения асинхронного динамического импорта
    await Promise.resolve();

    // Проверка вызова createRoot с правильным DOM элементом
    const { createRoot } = require('react-dom/client');
    expect(createRoot).toHaveBeenCalledWith(mockElement);
  });

  /**
   * Тест обработки отсутствующего DOM элемента
   * Проверяет, что функция корректно обрабатывает ситуацию, когда элемент не найден
   */
  test('должен выводить ошибку в консоль при отсутствии элемента', () => {
    // Настройка шпиона для console.error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    // Вызов функции с несуществующим ID элемента
    window.mountReactComponent('TestComponent', 'non-existent-id');

    // Проверка вывода ошибки в консоль с правильным сообщением
    expect(consoleSpy).toHaveBeenCalledWith('Element with id "non-existent-id" not found');

    // Восстановление оригинальной реализации console.error
    consoleSpy.mockRestore();
  });

  /**
   * Тест обработки ошибки загрузки компонента
   * Проверяет, что функция корректно обрабатывает ошибки при загрузке компонента
   */
  test('должен выводить ошибку в консоль при неудачной загрузке компонента', async () => {
    // Сохранение оригинальной функции console.error
    const originalConsoleError = console.error;

    // Создание мока для console.error
    const mockConsoleError = jest.fn();
    console.error = mockConsoleError;

    // Вызов функции с несуществующим компонентом
    window.mountReactComponent('NonExistentComponent', 'test-container');

    // Ожидание разрешения асинхронного динамического импорта и обработки ошибки
    await new Promise(resolve => setTimeout(resolve, 0));

    // Проверка вывода ошибки в консоль
    expect(mockConsoleError).toHaveBeenCalled();

    // Восстановление оригинальной функции console.error
    console.error = originalConsoleError;
  });
});
