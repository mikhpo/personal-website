import { useCallback, useEffect, useRef, useState } from 'react';
import Masonry from 'masonry-layout';

/**
 * Интервал дебаунса перед пересчетом раскладки и проявлением партии, в миллисекундах.
 */
const LAYOUT_DEBOUNCE_MS = 150;

/**
 * Пауза тишины после последнего события готовности, по истечении которой
 * возвращается плавная анимация перестановок, в миллисекундах.
 */
const ANIMATION_QUIET_MS = 500;

/**
 * Длительность анимации перестановок вне града загрузок.
 */
const ANIMATION_DURATION = '0.4s';

/**
 * Длительность анимации во время града загрузок: мгновенная расстановка,
 * чтобы не испытывать отмены и перезапуски переходов на каждом пересчете.
 */
const ANIMATION_INSTANT = '0';

/**
 * Хук для раскладки masonry-сетки через библиотеку masonry-layout.
 *
 * Инициализирует Masonry на контейнерном элементе после того, как в нем
 * отрисованы элементы, и пересчитывает раскладку по мере загрузки изображений.
 *
 * Ключевое правило: карточка не может стать видимой до пересчета, учтяшего
 * ее высоту. Пока изображение загружается, карточка прозрачна; событие
 * готовности лишь накапливается, и по дебаунсу выполняется пересчет, после
 * которого накопленная партия проявляется уже на финальных позициях.
 * Иначе карточка видима на позиции из раскладки с нулевыми высотами -
 * снимки наваливаются друг на друга стопкой, пока волна пересчетов
 * не разберет ее.
 *
 * Кэшированные изображения не поднимают событие load после монтирования,
 * поэтому после каждой смены списка завершенные изображения помечаются
 * готовыми отдельным проходом.
 *
 * При отсутствии элементов в контейнере (загрузка, ошибка, пустой список)
 * хук бездействует, при размонтировании сетки уничтожает экземпляр Masonry.
 *
 * @param {Array} items - Список элементов сетки; смена списка запускает пересчет
 * @return {Object} Реф контейнера, отметка готовности и множество проявленных id
 * @property {Object} containerRef - Реф для контейнерного элемента сетки
 * @property {Function} markImageReady - Отметить изображение элемента готовым
 *   (события load и error); вешается на изображения карточек
 * @property {Set<number>} revealedIds - Множество id элементов, проявленных
 *   после пересчета
 *
 * @example
 * const { containerRef, markImageReady, revealedIds } = useMasonry(photos);
 * return (
 *   <div ref={containerRef} className="masonry-grid">
 *     <div className="masonry-sizer" />
 *     {photos.map(photo => (
 *       <div key={photo.id} className="masonry-item" data-id={photo.id}>
 *         <PhotoCard
 *           photo={photo}
 *           revealed={revealedIds.has(photo.id)}
 *           onImageLoad={() => markImageReady(photo.id)}
 *         />
 *       </div>
 *     ))}
 *   </div>
 * );
 */
const useMasonry = (items) => {
  const containerRef = useRef(null);
  const masonryRef = useRef(null);
  const layoutTimerRef = useRef(null);
  const quietTimerRef = useRef(null);
  const readyIdsRef = useRef(new Set());
  const [revealedIds, setRevealedIds] = useState(() => new Set());

  /**
   * Приглушить анимацию перестановок: во время града загрузок раскладки
   * следуют друг за другом чаще длительности перехода, и анимация
   * отменялась бы и перезапускалась на каждом пересчете.
   * @function
   * @return {void}
   */
  const silenceAnimations = useCallback(() => {
    if (masonryRef.current) {
      masonryRef.current.options.transitionDuration = ANIMATION_INSTANT;
    }
  }, []);

  /**
   * Назначить возврат плавной анимации после паузы тишины в граде загрузок:
   * пагинация, фильтры и редкие догрузки продолжают переставляться плавно.
   * @function
   * @return {void}
   */
  const armAnimationTimer = useCallback(() => {
    clearTimeout(quietTimerRef.current);
    quietTimerRef.current = setTimeout(() => {
      if (masonryRef.current) {
        masonryRef.current.options.transitionDuration = ANIMATION_DURATION;
      }
    }, ANIMATION_QUIET_MS);
  }, []);

  /**
   * Отложенный пересчет раскладки Masonry и проявление накопленной партии:
   * серия событий готовности схлопывается в один пересчет по истечении паузы.
   * @function
   * @return {void}
   */
  const scheduleCommit = useCallback(() => {
    clearTimeout(layoutTimerRef.current);
    layoutTimerRef.current = setTimeout(() => {
      if (masonryRef.current) {
        masonryRef.current.layout();
      }
      if (readyIdsRef.current.size) {
        const ready = readyIdsRef.current;
        readyIdsRef.current = new Set();
        setRevealedIds((prev) => new Set([...prev, ...ready]));
      }
    }, LAYOUT_DEBOUNCE_MS);
  }, []);

  /**
   * Отметить изображение элемента готовым и назначить пересчет с проявлением:
   * приглушить анимацию, накопить готовность, пересчитать после паузы
   * и проявить накопленную партию на финальных позициях.
   * @function
   * @param {number} id - Идентификатор элемента сетки
   * @return {void}
   */
  const markImageReady = useCallback(
    (id) => {
      readyIdsRef.current.add(id);
      silenceAnimations();
      armAnimationTimer();
      scheduleCommit();
    },
    [silenceAnimations, armAnimationTimer, scheduleCommit],
  );

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }

    // Новая порция элементов - новый град загрузок: начинаем без анимации
    silenceAnimations();
    armAnimationTimer();

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
        transitionDuration: ANIMATION_INSTANT,
      });
    }

    // Кэшированные изображения не поднимут событие load после монтирования:
    // завершенные помечаются готовыми сразу после первичной раскладки
    container.querySelectorAll('.masonry-item').forEach((item) => {
      const img = item.querySelector('img');
      if (img && img.complete && img.naturalWidth > 0 && item.dataset.id !== undefined) {
        readyIdsRef.current.add(Number(item.dataset.id));
      }
    });

    scheduleCommit();

    return () => {
      clearTimeout(layoutTimerRef.current);
      clearTimeout(quietTimerRef.current);
      if (masonryRef.current) {
        masonryRef.current.destroy();
        masonryRef.current = null;
      }
    };
  }, [items, silenceAnimations, armAnimationTimer, scheduleCommit]);

  return { containerRef, markImageReady, revealedIds };
};

export default useMasonry;
