/**
 * Минимальная декларация глобального объекта bootstrap (js-бандл Bootstrap,
 * подключаемый Django-шаблоном). Покрывает фактическое использование:
 * программное открытие offcanvas-панели тегов.
 */

declare global {
  interface Window {
    bootstrap?: {
      Offcanvas: {
        getOrCreateInstance(element: Element): { show(): void };
      };
    };
  }
}

export {};
