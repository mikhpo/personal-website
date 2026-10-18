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

/** Элемент сетки с идентификатором для проявления после пересчета. */
interface MasonryItem {
  id: number;
}

/** Результат хука: реф контейнера, отметка готовности и проявленные id. */
export interface UseMasonryResult {
  containerRef: React.RefObject<HTMLDivElement | null>;
  markImageReady: (id: number) => void;
  revealedIds: Set<number>;
}

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
const useMasonry = <T extends MasonryItem>(items: T[]): UseMasonryResult => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const masonryRef = useRef<Masonry | null>(null);
  const layoutTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const quietTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const readyIdsRef = useRef(new Set<number>());
  const [revealedIds, setRevealedIds] = useState<Set<number>>(() => new Set());

  /**
   * Приглушить анимацию перестановок: во время града загрузок раскладки
   * следуют друг за другом чаще длительности перехода, и анимация
   * отменялась бы и перезапускалась на каждом пересчете.
   */
  const silenceAnimations = useCallback(() => {
    if (masonryRef.current) {
      masonryRef.current.options.transitionDuration = ANIMATION_INSTANT;
    }
  }, []);

  /**
   * Назначить возврат плавной анимации после паузы тишины в граде загрузок:
   * пагинация, фильтры и редкие догрузки продолжают переставляться плавно.
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
   */
  const markImageReady = useCallback(
    (id: number) => {
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
    container.querySelectorAll<HTMLElement>('.masonry-item').forEach((item) => {
      const img = item.querySelector<HTMLImageElement>('img');
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
