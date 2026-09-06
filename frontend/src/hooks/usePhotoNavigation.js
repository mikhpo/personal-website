import { useEffect, useRef } from 'react';
import { navigateTo } from '@services';

/** Минимальное горизонтальное смещение (в пикселях), распознаваемое как свайп. */
const SWIPE_THRESHOLD_PX = 50;

/**
 * Хук для переключения фотографий с клавиатуры и свайпами.
 *
 * Устанавливает обработчики на document:
 * - клавиши ArrowLeft/ArrowRight переходят к предыдущей/следующей фотографии;
 * - горизонтальный свайп влево/вправо на сенсорном экране переходит
 *   к следующей/предыдущей фотографии.
 *
 * Свайп распознается при горизонтальном смещении от SWIPE_THRESHOLD_PX
 * и преобладании горизонтальной составляющей над вертикальной, чтобы не
 * конфликтовать с вертикальной прокруткой. Multi-touch жесты (зум) игнорируются.
 *
 * Переход выполняется полной загрузкой страницы через navigateTo,
 * как при клике по обычной ссылке.
 *
 * @param {Object} options - Параметры хука
 * @param {string|null} options.previousUrl - URL предыдущей фотографии или null
 * @param {string|null} options.nextUrl - URL следующей фотографии или null
 * @param {boolean} [options.enabled=true] - Активны ли обработчики;
 *   при false нажатия клавиш и свайпы игнорируются
 *
 * @example
 * usePhotoNavigation({
 *   previousUrl: '/gallery/photo/1/',
 *   nextUrl: '/gallery/photo/3/',
 *   enabled: !showModal,
 * });
 */
const usePhotoNavigation = ({ previousUrl, nextUrl, enabled = true }) => {
  /** Точка начала касания { x, y } или null. */
  const touchStartRef = useRef(null);

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    const handleKeyDown = (event) => {
      // Не перехватывать браузерные комбинации с модификаторами.
      if (event.ctrlKey || event.altKey || event.metaKey || event.shiftKey) {
        return;
      }
      if (event.key === 'ArrowLeft' && previousUrl) {
        navigateTo(previousUrl);
      }
      if (event.key === 'ArrowRight' && nextUrl) {
        navigateTo(nextUrl);
      }
    };

    const handleTouchStart = (event) => {
      if (event.touches.length > 1) {
        touchStartRef.current = null;
        return;
      }
      const touch = event.touches[0];
      touchStartRef.current = { x: touch.clientX, y: touch.clientY };
    };

    const handleTouchEnd = (event) => {
      const start = touchStartRef.current;
      touchStartRef.current = null;
      if (!start) {
        return;
      }
      const touch = event.changedTouches[0];
      if (!touch) {
        return;
      }
      const dx = touch.clientX - start.x;
      const dy = touch.clientY - start.y;
      if (Math.abs(dx) < SWIPE_THRESHOLD_PX || Math.abs(dx) <= Math.abs(dy)) {
        return;
      }
      if (dx < 0 && nextUrl) {
        navigateTo(nextUrl);
      }
      if (dx > 0 && previousUrl) {
        navigateTo(previousUrl);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [previousUrl, nextUrl, enabled]);
};

export default usePhotoNavigation;
