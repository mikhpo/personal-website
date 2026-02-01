import { useCallback } from 'react';

/**
 * Хук для обработки открытия offcanvas панели
 *
 * @return {Function} Функция для открытия offcanvas панели
 */
const useOffcanvasHandler = () => {
  const openOffcanvas = useCallback((offcanvasId) => {
    const offcanvas = document.getElementById(offcanvasId);
    if (offcanvas) {
      // Используем Bootstrap JS API для открытия offcanvas
      const bootstrap = window.bootstrap;
      if (bootstrap && bootstrap.Offcanvas) {
        const offcanvasInstance = bootstrap.Offcanvas.getOrCreateInstance(offcanvas);
        offcanvasInstance.show();
      } else {
        // Fallback если Bootstrap JS не доступен
        offcanvas.classList.add('show');
        offcanvas.style.visibility = 'visible';
        offcanvas.setAttribute('aria-modal', 'true');
        offcanvas.setAttribute('role', 'dialog');
        document.body.classList.add('offcanvas-open');
      }
    }
  }, []);

  return { openOffcanvas };
};

export default useOffcanvasHandler;
