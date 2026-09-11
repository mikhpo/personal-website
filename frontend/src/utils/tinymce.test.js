/**
 * Тесты для конфигурации TinyMCE.
 *
 * Проверяет соответствие цветовой схемы редактора теме сайта.
 */

import { getEditorInit } from './tinymce';

describe('getEditorInit', () => {
  /**
   * Проверяет, что для темной темы используются темный скин и темные стили содержимого.
   */
  test('возвращает темную схему для темной темы', () => {
    const config = getEditorInit(true);
    expect(config.skin).toBe('oxide-dark');
    expect(config.content_css).toBe('dark');
  });

  /**
   * Проверяет, что для светлой темы используются светлый скин и стили по умолчанию.
   */
  test('возвращает светлую схему для светлой темы', () => {
    const config = getEditorInit(false);
    expect(config.skin).toBe('oxide');
    expect(config.content_css).toBe('default');
  });

  /**
   * Проверяет общие для обеих схем параметры: лицензию, плагины и панели инструментов.
   */
  test('содержит общие параметры редактора', () => {
    const config = getEditorInit(false);
    expect(config.license_key).toBe('gpl');
    expect(config.branding).toBe(false);
    expect(config.promotion).toBe(false);
    expect(config.plugins).toContain('image');
    expect(config.plugins).toContain('table');
    expect(config.toolbar1).toContain('fullscreen');
  });
});
