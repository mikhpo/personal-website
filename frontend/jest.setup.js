/**
 * @fileoverview Файл настройки Jest для тестирования компонентов React.
 *
 * Этот файл импортирует библиотеку @testing-library/jest-dom, которая предоставляет
 * дополнительные матчеры (matchers) для Jest, упрощающие тестирование компонентов DOM.
 *
 * Матчеры позволяют использовать такие выражения, как:
 * - toBeInTheDocument() - проверяет, что элемент присутствует в DOM
 * - toHaveClass() - проверяет, что элемент имеет определенный CSS класс
 * - toHaveAttribute() - проверяет наличие атрибута у элемента
 *
 * Подробнее о доступных матчерах можно узнать в документации:
 * https://github.com/testing-library/jest-dom
 */

import '@testing-library/jest-dom';

// В браузере window.matchMedia сообщает, включена ли темная тема в настройках
// системы, - сайт использует этот вызов, чтобы определить тему пользователя.
// Тесты выполняются не в браузере, а в jsdom - эмуляторе браузера для Jest,
// у которого matchMedia отсутствует: без этого блока рендер навигационной
// панели завершался бы ошибкой "window.matchMedia is not a function".
// Блок подменяет matchMedia фальшивой функцией, которая всегда отвечает,
// что в системе включена светлая тема (matches: false).
// Флаги writable и configurable разрешают такую подмену: отдельные тесты
// устанавливают собственный вариант стаба, чтобы проверить темную тему.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  configurable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
