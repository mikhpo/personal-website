import { renderHook, fireEvent } from '@testing-library/react';

jest.mock('@services/navigation');

import { navigateTo } from '@services';
import usePhotoNavigation from './usePhotoNavigation';

/**
 * Тесты для хука usePhotoNavigation.
 *
 * Проверяют переключение фотографий клавишами ArrowLeft/ArrowRight
 * и горизонтальными свайпами, а также условия игнорирования:
 * отсутствие соседней фотографии, отключение хука, модификаторы,
 * короткие и вертикальные свайпы, multi-touch.
 */
describe('usePhotoNavigation', () => {
  const previousUrl = '/gallery/photo/1/';
  const nextUrl = '/gallery/photo/3/';

  const renderNavigation = (options = {}) => renderHook(
    (props) => usePhotoNavigation({ previousUrl, nextUrl, ...props }),
    { initialProps: options }
  );

  beforeEach(() => {
    navigateTo.mockClear();
  });

  /**
   * Проверяет навигацию с клавиатуры.
   */
  describe('клавиатура', () => {
    test('ArrowLeft переходит к предыдущей фотографии', () => {
      renderNavigation();

      fireEvent.keyDown(document, { key: 'ArrowLeft' });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith(previousUrl);
    });

    test('ArrowRight переходит к следующей фотографии', () => {
      renderNavigation();

      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith(nextUrl);
    });

    test('другие клавиши игнорируются', () => {
      renderNavigation();

      fireEvent.keyDown(document, { key: 'ArrowUp' });
      fireEvent.keyDown(document, { key: 'Enter' });
      fireEvent.keyDown(document, { key: 'a' });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test.each([
      ['ctrlKey', { ctrlKey: true }],
      ['altKey', { altKey: true }],
      ['metaKey', { metaKey: true }],
      ['shiftKey', { shiftKey: true }],
    ])('стрелки с модификатором %s игнорируются', (modifier, extra) => {
      renderNavigation();

      fireEvent.keyDown(document, { key: 'ArrowLeft', ...extra });
      fireEvent.keyDown(document, { key: 'ArrowRight', ...extra });

      expect(navigateTo).not.toHaveBeenCalled();
    });
  });

  /**
   * Проверяет учет отсутствующих соседних фотографий.
   */
  describe('отсутствующие соседние фотографии', () => {
    test('ArrowLeft без предыдущей фотографии не выполняет переход', () => {
      renderNavigation({ previousUrl: null });

      fireEvent.keyDown(document, { key: 'ArrowLeft' });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('ArrowRight без следующей фотографии не выполняет переход', () => {
      renderNavigation({ nextUrl: null });

      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('свайп влево без следующей фотографии не выполняет переход', () => {
      renderNavigation({ nextUrl: null });

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('свайп вправо без предыдущей фотографии не выполняет переход', () => {
      renderNavigation({ previousUrl: null });

      fireEvent.touchStart(document, { touches: [{ clientX: 100, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 220, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });
  });

  /**
   * Проверяет переключение параметром enabled.
   */
  describe('отключение хука', () => {
    test('enabled=false отключает навигацию с клавиатуры', () => {
      renderNavigation({ enabled: false });

      fireEvent.keyDown(document, { key: 'ArrowLeft' });
      fireEvent.keyDown(document, { key: 'ArrowRight' });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('enabled=false отключает навигацию свайпами', () => {
      renderNavigation({ enabled: false });

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('включение после отключения восстанавливает навигацию', () => {
      const { rerender } = renderNavigation({ enabled: false });

      fireEvent.keyDown(document, { key: 'ArrowRight' });
      expect(navigateTo).not.toHaveBeenCalled();

      rerender({ previousUrl, nextUrl, enabled: true });

      fireEvent.keyDown(document, { key: 'ArrowRight' });
      expect(navigateTo).toHaveBeenCalledWith(nextUrl);
    });
  });

  /**
   * Проверяет навигацию свайпами на сенсорных экранах.
   */
  describe('свайпы', () => {
    test('свайп влево переходит к следующей фотографии', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith(nextUrl);
    });

    test('свайп вправо переходит к предыдущей фотографии', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 100, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 220, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith(previousUrl);
    });

    test('короткий горизонтальный свайп игнорируется', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 100, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 60, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('вертикально доминирующее касание игнорируется', () => {
      renderNavigation();

      // Горизонтальное смещение превышает порог, но вертикальное больше.
      fireEvent.touchStart(document, { touches: [{ clientX: 100, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 200, clientY: 250 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('свайп ровно на пороговом расстоянии распознается', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 150, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
      expect(navigateTo).toHaveBeenCalledWith(nextUrl);
    });

    test('multi-touch жест игнорируется', () => {
      renderNavigation();

      fireEvent.touchStart(document, {
        touches: [
          { clientX: 200, clientY: 100 },
          { clientX: 300, clientY: 200 },
        ],
      });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('touchend без зафиксированного touchstart игнорируется', () => {
      renderNavigation();

      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('touchend без changedTouches игнорируется', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, {});

      expect(navigateTo).not.toHaveBeenCalled();
    });

    test('второй свайп после первого работает от новой точки касания', () => {
      renderNavigation();

      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });
      expect(navigateTo).toHaveBeenCalledTimes(1);

      // Короткое касание от старой точки не должно сработать,
      // свайп считается только от новой точки touchstart.
      fireEvent.touchStart(document, { touches: [{ clientX: 110, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Проверяет снятие обработчиков после размонтирования.
   */
  describe('очистка обработчиков', () => {
    test('после размонтирования события не обрабатываются', () => {
      const { unmount } = renderNavigation();

      unmount();

      fireEvent.keyDown(document, { key: 'ArrowRight' });
      fireEvent.touchStart(document, { touches: [{ clientX: 200, clientY: 100 }] });
      fireEvent.touchEnd(document, { changedTouches: [{ clientX: 100, clientY: 100 }] });

      expect(navigateTo).not.toHaveBeenCalled();
    });
  });
});
