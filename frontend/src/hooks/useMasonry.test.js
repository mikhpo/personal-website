import React from 'react';
import { render, act } from '@testing-library/react';
import useMasonry from './useMasonry';

// Геометрия тестовой сетки: контейнер 1000px вмещает 4 колонки по 235px с желобом 24px
const CONTAINER_WIDTH = 1000;
const COLUMN_WIDTH = 235;
const GUTTER = 24;
const COLUMN_STEP = COLUMN_WIDTH + GUTTER;

// Ссылка на актуальный scheduleLayout из пробника
const scheduleLayoutRef = { current: null };

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
  const { containerRef, scheduleLayout } = useMasonry(items);
  scheduleLayoutRef.current = scheduleLayout;
  return (
    <div ref={containerRef} className="masonry-grid" data-mock-width={CONTAINER_WIDTH}>
      <div className="masonry-sizer" data-mock-width={COLUMN_WIDTH} />
      {items.map((item) => (
        <div
          key={item.id}
          className="masonry-item"
          data-mock-width={COLUMN_WIDTH}
          data-mock-height={item.height}
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
 * с подмененными габаритами элементов библиотека выполняет настоящую раскладку,
 * и тестируются свойства результата - выравнивание по колонкам, отсутствие
 * наложений, плотная упаковка короткой колонки, перестроение при догрузке
 * изображений, высота сетки.
 */
describe('useMasonry', () => {
  // Финальные высоты шести карточек: последняя пара проверяет упаковку в короткие колонки
  const loadedHeights = [300, 500, 200, 400, 250, 600];

  beforeEach(() => {
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

  test('упаковывает элементы в четыре колонки без наложений', () => {
    const { container } = render(
      <HookProbe items={loadedHeights.map((height, index) => ({ id: index + 1, height }))} />,
    );

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

    // Карточки 4 и 5 встали в самые короткие на тот момент колонки
    // (под карточки 3 и 1), а не в очередные по порядку;
    // вертикальный зазор между карточками дает CSS margin-bottom браузера,
    // в jsdom он нулевой, поэтому карточки примыкают вплотную
    const third = rects[2];
    const fourth = rects[3];
    expect(fourth.x).toBe(third.x);
    expect(fourth.y).toBe(third.y + third.height);

    const first = rects[0];
    const fifth = rects[4];
    expect(fifth.x).toBe(first.x);
    expect(fifth.y).toBe(first.y + first.height);

    // Высота сетки равна высоте самой высокой колонки: 500 + 600
    const grid = container.querySelector('.masonry-grid');
    expect(grid.style.height).toBe(`${loadedHeights[1] + loadedHeights[5]}px`);
  });

  test('перестраивает сетку при догрузке изображений', () => {
    // Миниатюры еще не загружены: карточки схлопнуты до заглушки 100px
    const { container } = render(
      <HookProbe items={loadedHeights.map((height, index) => ({ id: index + 1, height: 100 }))} />,
    );

    const itemElements = [...container.querySelectorAll('.masonry-item')];
    const grid = container.querySelector('.masonry-grid');

    // Схлопнутые карточки заняли верхний ряд, сетка низкая
    expect(grid.style.height).toBe('200px');

    // Картинки загрузились: высоты карточек выросли вне React, как в браузере,
    // и каждая карточка подняла событие загрузки
    jest.useFakeTimers();
    act(() => {
      itemElements.forEach((element, index) => {
        element.setAttribute('data-mock-height', String(loadedHeights[index]));
        scheduleLayoutRef.current();
      });
      jest.advanceTimersByTime(150);
    });

    // В браузере перестроение анимируется, и финальные позиции фиксируются
    // по завершении перехода - доводим анимацию до конца
    act(() => {
      itemElements.forEach((element) => {
        const event = new Event('transitionend');
        event.propertyName = 'transform';
        element.dispatchEvent(event);
      });
    });

    // Сетка перестроилась под реальные пропорции: карточка 5 встала вплотную
    // под карточку 1 в ее колонке, высота сетки стала высотой самой высокой колонки
    const first = itemElements[0];
    const fifth = itemElements[4];
    expect(readPosition(fifth).x).toBe(readPosition(first).x);
    expect(readPosition(fifth).y).toBe(300);
    expect(grid.style.height).toBe(`${loadedHeights[1] + loadedHeights[5]}px`);
  });

  test('проходит полный жизненный цикл сетки без ошибок', () => {
    const items = loadedHeights.map((height, index) => ({ id: index + 1, height }));
    const { rerender, unmount } = render(<HookProbe items={items} />);

    rerender(<HookProbe items={[...items, { id: 7, height: 350 }]} />);
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
