/**
 * Локальная декларация masonry-layout.
 *
 * @types/masonry-layout объявляет все методы опциональными и использует any
 * (transitionDuration), вынуждая условные вызовы у стабильно существующих
 * методов; декларация покрывает только фактическое использование хуком
 * useMasonry: конструктор, layout, reloadItems, destroy и опции инициализации.
 */

declare module 'masonry-layout' {
  interface MasonryOptions {
    itemSelector?: string;
    columnWidth?: string | number | Element;
    percentPosition?: boolean;
    gutter?: number;
    transitionDuration?: string;
  }

  class Masonry {
    constructor(element: Element, options?: MasonryOptions);
    options: MasonryOptions;
    layout(): void;
    reloadItems(): void;
    destroy(): void;
  }

  export default Masonry;
}
