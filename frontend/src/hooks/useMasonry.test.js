import React from 'react';
import { render, act } from '@testing-library/react';
import useMasonry from './useMasonry';

// Геометрия тестовой сетки: контейнер 1000px вмещает ровно 4 колонки
// по 232px с желобом 24px (4 x 232 + 3 x 24 = 1000)
const CONTAINER_WIDTH = 1000;
const COLUMN_WIDTH = 232;
const GUTTER = 24;
const COLUMN_STEP = COLUMN_WIDTH + GUTTER;

// Ссылка на актуальный markImageReady из пробника
const markImageReadyRef = { current: null };

/**
 * Пробник хука useMasonry: рендерит masonry-структуру как в списках галереи.
 * Атрибуты data-mock-width/data-mock-height задают габариты элементов:
 * jsdom не вычисляет размеры сам, тесты подменяют замеры на эти значения.
 *
 * @param {Object} props - Пропсы компонента
 * @param {Array} props.items - Элементы сетки с высотой: { id, name, height }
 * @return {JSX.Element} masonry-сетка
 */
const HookProbe = ({ items }) => {
  const { containerRef, markImageReady, revealedIds } = useMasonry(items);
  markImageReadyRef.current = markImageReady;
  return (
    <div ref={containerRef} className="masonry-grid" data-mock-width={CONTAINER_WIDTH}>
      <div className="masonry-sizer" data-mock-width={COLUMN_WIDTH} />
      {items.map((item) => (
        <div
          key={item.id}
          className={`masonry-item ${revealedIds.has(item.id) ? 'is-visible' : ''}`}
          data-mock-width={COLUMN_WIDTH}
          data-mock-height={item.height}
          data-id={item.id}
        >
          {item.name}
        </div>
      ))}
    </div>
  );
};

/**
 * Прочитать координаты элемента из стилей, выставленных Masonry.
 * Позиция может быть в transform (translate/translate3d) или в left/top,
 * с percentPosition горизонталь задается процентами от ширины контейнера.
 *
 * @param {HTMLElement} element - Элемент сетки
 * @return {Object} Координаты в пикселях: { x, y }
 */
const readPosition = (element) => {
  const transform = element.style.transform;
  if (transform && transform !== 'none') {
    const match = transform.match(/translate(?:3d)?\(\s*(-?[\d.]+)px\s*,\s*(-?[\d.]+)px/);
    if (match) {
      return { x: parseFloat(match[1]), y: parseFloat(match[2]) };
    }
  }

  const parseCoordinate = (raw) => {
    if (!raw) {
      return Number.NaN;
    }
    const value = parseFloat(raw);
    return raw.includes('%') ? Math.round((value / 100) * CONTAINER_WIDTH) : value;
  };

  return { x: parseCoordinate(element.style.left), y: parseCoordinate(element.style.top) };
};

/**
 * Тесты для хука useMasonry.
 *
 * Проверяют поведение сетки, видимое посетителю, на реальном masonry-layout:
 * с подмененными габаритами элементов библиотека выполняет настоящую
 * раскладку, и тестируются свойства результата - карточка появляется только
 * после пересчета, учтяшего ее высоту; проявленные карточки выровнены по
 * колонкам и не пересекаются; высота сетки соответствует содержимому.
 */
describe('useMasonry', () => {
  // Финальные высоты шести карточек: последняя пара проверяет упаковку в короткие колонки
  const loadedHeights = [300, 500, 200, 400, 250, 600];
  const probeItems = loadedHeights.map((height, index) => ({ id: index + 1, height }));

  beforeEach(() => {
    jest.useFakeTimers();
    jest.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockImplementation(function mockWidth() {
      return parseInt(this.dataset.mockWidth, 10) || 0;
    });
    jest.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockImplementation(function mockHeight() {
      return parseInt(this.dataset.mockHeight, 10) || 0;
    });
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  test('скрывает карточки до первого пересчета и проявляет после', () => {
    const { container } = render(<HookProbe items={probeItems} />);

    // Сразу после монтирования ни одна карточка не проявлена:
    // первичная раскладка не знает их высот
    const gridItems = [...container.querySelectorAll('.masonry-item')];
    gridItems.forEach((item) => {
      expect(item).not.toHaveClass('is-visible');
    });

    // Отметить все изображения готовыми и дождаться контрольного пересчета
    act(() => {
      gridItems.forEach((_, index) => markImageReadyRef.current(index + 1));
      jest.advanceTimersByTime(150);
    });

    gridItems.forEach((item) => {
      expect(item).toHaveClass('is-visible');
    });
  });

  test('упаковывает проявленные карточки в четыре колонки без наложений', () => {
    const { container } = render(<HookProbe items={probeItems} />);

    act(() => {
      probeItems.forEach((_, index) => markImageReadyRef.current(index + 1));
      jest.advanceTimersByTime(150);
    });

    const itemElements = [...container.querySelectorAll('.masonry-item')];
    expect(itemElements).toHaveLength(loadedHeights.length);

    const rects = itemElements.map((element, index) => {
      const { x, y } = readPosition(element);
      return { x, y, width: COLUMN_WIDTH, height: loadedHeights[index] };
    });

    // Позиции всех элементов вычислены
    rects.forEach(({ x, y }) => {
      expect(Number.isFinite(x)).toBe(true);
      expect(Number.isFinite(y)).toBe(true);
    });

    // Все элементы выровнены по четырем колонкам сетки
    const columnXs = [0, 1, 2, 3].map((column) => column * COLUMN_STEP);
    rects.forEach(({ x }) => {
      expect(columnXs).toContain(x);
    });

    // Первые четыре карточки заняли четыре разные колонки
    const firstRowXs = rects.slice(0, 4).map(({ x }) => x);
    expect(new Set(firstRowXs).size).toBe(4);

    // Никакие два элемента не пересекаются: прямоугольники разделены,
    // если один из них целиком выше, ниже, левее или правее другого,
    // поэтому четыре условия соединены через ИЛИ
    for (let i = 0; i < rects.length; i += 1) {
      for (let j = i + 1; j < rects.length; j += 1) {
        const a = rects[i];
        const b = rects[j];
        const separated =
          a.x + a.width <= b.x ||
          b.x + b.width <= a.x ||
          a.y + a.height <= b.y ||
          b.y + b.height <= a.y;
        expect(separated).toBe(true);
      }
    }

    // Карточки 5 и 6 встали в самые короткие на тот момент колонки
    // (под карточки 3 и 1), а не в очередные по порядку;
    // вертикальный зазор между карточками дает CSS margin-bottom браузера,
    // в jsdom он нулевой, поэтому карточки примыкают вплотную
    const third = rects[2];
    const fifth = rects[4];
    expect(fifth.x).toBe(third.x);
    expect(fifth.y).toBe(third.y + third.height);

    const first = rects[0];
    const sixth = rects[5];
    expect(sixth.x).toBe(first.x);
    expect(sixth.y).toBe(first.y + first.height);

    // Высота сетки равна высоте самой высокой колонки: 300 + 600
    const grid = container.querySelector('.masonry-grid');
    expect(grid.style.height).toBe(`${loadedHeights[0] + loadedHeights[5]}px`);
  });

  test('проявляет догрузившиеся карточки отдельным пересчетом при смене списка', () => {
    const { container, rerender } = render(<HookProbe items={probeItems} />);

    act(() => {
      probeItems.forEach((_, index) => markImageReadyRef.current(index + 1));
      jest.advanceTimersByTime(150);
    });

    const newItems = [...probeItems, { id: 7, height: 350 }];
    rerender(<HookProbe items={newItems} />);

    // Карточка новой порции скрыта, пока ее изображение не готово
    const seventh = [...container.querySelectorAll('.masonry-item')][6];
    expect(seventh).not.toHaveClass('is-visible');

    act(() => {
      markImageReadyRef.current(7);
      jest.advanceTimersByTime(150);
    });

    expect(seventh).toHaveClass('is-visible');
  });

  test('проходит полный жизненный цикл сетки без ошибок', () => {
    const { rerender, unmount } = render(<HookProbe items={probeItems} />);

    const newItems = [...probeItems, { id: 7, height: 350 }];
    rerender(<HookProbe items={newItems} />);
    unmount();
  });

  test('хук бездействует, когда контейнер не в DOM', () => {
    const EmptyProbe = () => {
      const { containerRef } = useMasonry([]);
      return (
        <div>
          {false && <div ref={containerRef} className="masonry-grid" />}
          Пусто
        </div>
      );
    };

    render(<EmptyProbe />);
  });
});
