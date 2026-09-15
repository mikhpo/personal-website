import { useCallback, useEffect, useRef } from 'react';
import Masonry from 'masonry-layout';

/**
 * Интервал дебаунса перед пересчетом раскладки Masonry, в миллисекундах.
 * Схлопывает серию событий загрузки изображений в один пересчет.
 */
const LAYOUT_DEBOUNCE_MS = 150;

/**
 * Хук для раскладки masonry-сетки через библиотеку masonry-layout.
 *
 * Инициализирует Masonry на контейнерном элементе после того, как в нем
 * отрисованы элементы, пересчитывает раскладку при смене списка и при
 * догрузке изображений. Высоты картинок с loading="lazy" известны только
 * после загрузки, поэтому сетка уточняется прогрессно: по событию onLoad
 * каждой картинки (scheduleLayout) и одним пересчетом после смены списка,
 * закрывающим уже кэшированные изображения.
 *
 * При отсутствии элементов в контейнере (загрузка, ошибка, пустой список)
 * хук бездействует, при размонтировании сетки уничтожает экземпляр Masonry.
 *
 * @param {Array} items - Список элементов сетки; смена списка запускает пересчет
 * @return {Object} Реф контейнера и функция отложенного пересчета раскладки
 * @property {Object} containerRef - Реф для контейнерного элемента сетки
 * @property {Function} scheduleLayout - Отложенный пересчет раскладки; вешается
 *   на onLoad и onError изображений
 *
 * @example
 * const { containerRef, scheduleLayout } = useMasonry(photos);
 * return (
 *   <div ref={containerRef} className="masonry-grid">
 *     <div className="masonry-sizer" />
 *     {photos.map(photo => (
 *       <div key={photo.id} className="masonry-item">
 *         <PhotoCard photo={photo} onImageLoad={scheduleLayout} />
 *       </div>
 *     ))}
 *   </div>
 * );
 */
const useMasonry = (items) => {
  const containerRef = useRef(null);
  const masonryRef = useRef(null);
  const layoutTimerRef = useRef(null);

  /**
   * Отложенный пересчет раскладки Masonry: серия событий загрузки картинок
   * схлопывается в один пересчет по истечении паузы после последнего события.
   * @function
   * @return {void}
   */
  const scheduleLayout = useCallback(() => {
    clearTimeout(layoutTimerRef.current);
    layoutTimerRef.current = setTimeout(() => {
      if (masonryRef.current) {
        masonryRef.current.layout();
      }
    }, LAYOUT_DEBOUNCE_MS);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }

    if (masonryRef.current) {
      // Список изменился при живой сетке: перечитать элементы и пересчитать
      masonryRef.current.reloadItems();
      masonryRef.current.layout();
    } else {
      masonryRef.current = new Masonry(container, {
        itemSelector: '.masonry-item',
        columnWidth: '.masonry-sizer',
        percentPosition: true,
        gutter: 24,
      });
    }

    // Уже загруженные (кэшированные) картинки событие load не поднимут,
    // поэтому после каждой смены списка назначается контрольный пересчет
    scheduleLayout();

    return () => {
      clearTimeout(layoutTimerRef.current);
      if (masonryRef.current) {
        masonryRef.current.destroy();
        masonryRef.current = null;
      }
    };
  }, [items, scheduleLayout]);

  return { containerRef, scheduleLayout };
};

export default useMasonry;
