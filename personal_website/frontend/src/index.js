import React from 'react';
import { createRoot } from 'react-dom/client';

// Импорт Alert компонентов
import Alert from '@components/Alert/AlertDetail';
import AlertList from '@components/Alert/AlertList';

// Импорт Gallery компонентов
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import AlbumList from '@components/Gallery/Album/AlbumList';
import PhotoDetail from '@components/Gallery/Photo/PhotoDetail/PhotoDetail';
import PhotoList from '@components/Gallery/Photo/PhotoList';
import ExifData from '@components/Gallery/Photo/ExifData';
import PhotoTags from '@components/Gallery/Photo/PhotoTags';
import PhotoNavigation from '@components/Gallery/Photo/PhotoNavigation';
import TagButton from '@components/Gallery/Tags/TagButton';
import TagsOffcanvas from '@components/Gallery/Tags/TagsOffcanvas';
import AlbumSelector from '@components/Gallery/Upload/AlbumSelector';
import FileDropzone from '@components/Gallery/Upload/FileDropzone';
import UploadProgress from '@components/Gallery/Upload/UploadProgress';
import PhotoUploadForm from '@components/Gallery/Upload/PhotoUploadForm';

/**
 * Реестр зарегистрированных компонентов
 *
 * @description
 * Содержит все предзагруженные компоненты для быстрого доступа
 */
const componentRegistry = {
  // Alert components
  'Alert/Alert': Alert,
  'Alert/AlertList': AlertList,
  
  // Gallery components
  'Gallery/AlbumCard': AlbumCard,
  'Gallery/AlbumList': AlbumList,
  'Gallery/PhotoDetail': PhotoDetail,
  'Gallery/PhotoList': PhotoList,
  'Gallery/ExifData': ExifData,
  'Gallery/PhotoTags': PhotoTags,
  'Gallery/PhotoNavigation': PhotoNavigation,
  'Gallery/TagButton': TagButton,
  'Gallery/TagsOffcanvas': TagsOffcanvas,
  'Gallery/AlbumSelector': AlbumSelector,
  'Gallery/FileDropzone': FileDropzone,
  'Gallery/UploadProgress': UploadProgress,
  'Gallery/PhotoUploadForm': PhotoUploadForm,
};

/**
 * Функция для монтирования React компонентов
 *
 * @description
 * Монтирует React компонент в указанный DOM элемент.
 * Сначала проверяет реестр предзагруженных компонентов, затем пытается динамический импорт.
 *
 * @param {string} componentName - Имя компонента (например, 'Gallery/AlbumList' или 'TestComponent')
 * @param {string} elementId - ID DOM элемента, в который будет смонтирован компонент
 * @param {Object} [props={}] - Свойства, передаваемые компоненту
 *
 * @example
 * // Монтирование предзагруженного компонента
 * window.mountReactComponent('Gallery/AlbumList', 'album-list-root', { apiUrl: '/api/albums/' });
 *
 * // Монтирование динамически загружаемого компонента
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

  // Проверить реестр предзагруженных компонентов
  if (componentRegistry[componentName]) {
    const Component = componentRegistry[componentName];
    root.render(React.createElement(Component, props));
    return;
  }

  // Попытка динамического импорта для компонентов не из реестра
  import(`@components/${componentName}.jsx`)
    .then((module) => {
      const Component = module.default;
      root.render(React.createElement(Component, props));
    })
    .catch((error) => {
      console.error(`Failed to load component "${componentName}":`, error);
    });
};

console.log('React runtime loaded successfully');
