import React from 'react';
import { createRoot } from 'react-dom/client';

/**
 * Функция для монтирования React компонентов
 *
 * @description
 * Динамически загружает и монтирует React компонент в указанный DOM элемент.
 * Компоненты загружаются из директории ./components/ с использованием динамического импорта.
 *
 * @param {string} componentName - Имя компонента для загрузки (без расширения файла)
 * @param {string} elementId - ID DOM элемента, в который будет смонтирован компонент
 * @param {Object} [props={}] - Свойства, передаваемые компоненту
 *
 * @example
 * // Монтирование компонента TestComponent в элемент с ID 'test-container'
 * window.mountReactComponent('TestComponent', 'test-container', { title: 'Пример' });
 *
 * @return {void}
 */
window.mountReactComponent = (componentName, elementId, props = {}) => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return;
  }

  const root = createRoot(element);

  /**
   * Динамический импорт компонентов
   *
   * @description
   * Загружает компонент по имени из директории ./components/
   * Ожидается, что компонент экспортируется как default export
   */
  import(`./components/${componentName}`).then((module) => {
    const Component = module.default;
    root.render(React.createElement(Component, props));
  }).catch((error) => {
    console.error(`Failed to load component "${componentName}":`, error);
  });
};

console.log('React runtime loaded successfully');
