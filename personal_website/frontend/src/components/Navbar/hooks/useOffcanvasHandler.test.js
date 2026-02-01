import { renderHook, act } from '@testing-library/react';
import useOffcanvasHandler from './useOffcanvasHandler';

/**
 * Тесты для хука useOffcanvasHandler
 *
 * Данные тесты проверяют корректность работы хука для открытия offcanvas панели
 *
 * @module useOffcanvasHandler.test
 * @description Тестирование хука useOffcanvasHandler
 */
describe('useOffcanvasHandler', () => {
  /**
   * Тест проверяет корректность получения функции openOffcanvas из хука
   *
   * Проверяет:
   * - Наличие функции openOffcanvas в возвращаемом результате
   * - Тип функции openOffcanvas
   *
   * @function
   * @name returns-openOffcanvas-function
   */
  test('возвращает функцию openOffcanvas', () => {
    const { result } = renderHook(() => useOffcanvasHandler());

    expect(result.current.openOffcanvas).toBeDefined();
    expect(typeof result.current.openOffcanvas).toBe('function');
  });

  /**
   * Тест проверяет корректность открытия offcanvas панели через Bootstrap API
   *
   * Проверяет:
   * - Вызов Bootstrap Offcanvas API при наличии элемента
   * - Корректность передачи элемента в getOrCreateInstance
   * - Вызов метода show у инстанса offcanvas
   *
   * @function
   * @name opens-offcanvas-using-bootstrap-api
   */
  test('открывает offcanvas панель используя Bootstrap API', () => {
    // Мокируем window.bootstrap
    const mockOffcanvasInstance = {
      show: jest.fn(),
    };

    const mockBootstrap = {
      Offcanvas: {
        getOrCreateInstance: jest.fn(() => mockOffcanvasInstance),
      },
    };

    Object.defineProperty(window, 'bootstrap', {
      value: mockBootstrap,
      writable: true,
    });

    // Мокируем document.getElementById
    const mockOffcanvasElement = document.createElement('div');
    mockOffcanvasElement.id = 'tagsOffcanvas';
    document.getElementById = jest.fn(() => mockOffcanvasElement);

    const { result } = renderHook(() => useOffcanvasHandler());

    act(() => {
      result.current.openOffcanvas('tagsOffcanvas');
    });

    // Проверяем, что были вызваны соответствующие функции
    expect(document.getElementById).toHaveBeenCalledWith('tagsOffcanvas');
    expect(mockBootstrap.Offcanvas.getOrCreateInstance).toHaveBeenCalledWith(mockOffcanvasElement);
    expect(mockOffcanvasInstance.show).toHaveBeenCalled();
  });

  /**
   * Тест проверяет fallback поведение при отсутствии Bootstrap API
   *
   * Проверяет:
   * - Добавление класса 'show' к элементу offcanvas
   * - Установку видимости элемента
   * - Добавление атрибутов aria-modal и role
   * - Добавление класса 'offcanvas-open' к body
   *
   * @function
   * @name falls-back-when-bootstrap-not-available
   */
  test('использует fallback когда Bootstrap API недоступен', () => {
    // Удаляем window.bootstrap
    Object.defineProperty(window, 'bootstrap', {
      value: undefined,
      writable: true,
    });

    // Мокируем document.getElementById
    const mockOffcanvasElement = document.createElement('div');
    mockOffcanvasElement.id = 'tagsOffcanvas';
    document.getElementById = jest.fn(() => mockOffcanvasElement);

    // Мокируем document.body.classList.add
    document.body.classList.add = jest.fn();

    const { result } = renderHook(() => useOffcanvasHandler());

    act(() => {
      result.current.openOffcanvas('tagsOffcanvas');
    });

    // Проверяем fallback поведение
    expect(mockOffcanvasElement.classList.contains('show')).toBe(true);
    expect(mockOffcanvasElement.style.visibility).toBe('visible');
    expect(mockOffcanvasElement.getAttribute('aria-modal')).toBe('true');
    expect(mockOffcanvasElement.getAttribute('role')).toBe('dialog');
    expect(document.body.classList.add).toHaveBeenCalledWith('offcanvas-open');
  });

  /**
   * Тест проверяет поведение при отсутствии элемента offcanvas
   *
   * Проверяет:
   * - Отсутствие ошибок при отсутствии элемента
   * - Не вызываются методы Bootstrap API
   *
   * @function
   * @name handles-missing-offcanvas-element
   */
  test('корректно обрабатывает отсутствие элемента offcanvas', () => {
    // Мокируем document.getElementById чтобы возвращал null
    document.getElementById = jest.fn(() => null);

    const { result } = renderHook(() => useOffcanvasHandler());

    // Не должно быть ошибок
    expect(() => {
      act(() => {
        result.current.openOffcanvas('nonexistent');
      });
    }).not.toThrow();
  });
});
