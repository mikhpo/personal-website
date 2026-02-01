import {
  createFirstPageElements,
  createMainPageElements,
  createLastPageElements
} from './pageItemsGenerator';

/**
 * Тесты для генератора элементов пагинации
 *
 * Модуль тестирует функции создания элементов пагинации:
 * - createFirstPageElements: создание элементов первой страницы и многоточия в начале
 * - createMainPageElements: создание элементов для основного диапазона страниц
 * - createLastPageElements: создание элементов последней страницы и многоточия в конце
 */
describe('pageItemsGenerator', () => {
  // Mock функция для создания элементов
  const mockCreateElement = jest.fn((type, page) => ({ type, page }));

  beforeEach(() => {
    mockCreateElement.mockClear();
  });

  /**
   * Тесты для функции createFirstPageElements
   *
   * Функция создает элемент первой страницы и многоточие в начале пагинации
   * при необходимости (когда начальная страница основного диапазона > 1)
   */
  describe('createFirstPageElements', () => {
    /**
     * Тест проверяет, что при startPage=3 и totalPages=10 создаются:
     * 1. Элемент первой страницы (так как startPage > 1)
     * 2. Многоточие в начале (так как startPage > 2)
     *
     * Это соответствует ситуации, когда текущая страница находится в середине,
     * и нужно показать ссылку на первую страницу и многоточие перед основным диапазоном.
     */
    test('создает элемент первой страницы и многоточие при необходимости', () => {
      const result = createFirstPageElements(3, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(2);
      expect(mockCreateElement).toHaveBeenCalledWith('first-page');
      expect(mockCreateElement).toHaveBeenCalledWith('ellipsis-start');
    });

    /**
     * Тест проверяет, что при startPage=1 не создаются никакие элементы,
     * так как первая страница уже включена в основной диапазон страниц.
     *
     * Это соответствует ситуации, когда текущая страница близка к началу,
     * и первая страница отображается в основном диапазоне.
     */
    test('не создает элементы, если startPage равен 1', () => {
      const result = createFirstPageElements(1, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(0);
      expect(mockCreateElement).not.toHaveBeenCalled();
    });

    /**
     * Тест проверяет, что при startPage=2 создается только элемент первой страницы,
     * но не многоточие, так как между первой и второй страницами нет промежутка.
     *
     * Это соответствует ситуации, когда текущая страница вторая,
     * и первая страница отображается отдельно, но без многоточия.
     */
    test('создает только элемент первой страницы, если startPage равен 2', () => {
      const result = createFirstPageElements(2, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(1);
      expect(mockCreateElement).toHaveBeenCalledWith('first-page');
      expect(mockCreateElement).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Тесты для функции createMainPageElements
   *
   * Функция создает элементы страниц для основного диапазона страниц
   * от startPage до endPage включительно
   */
  describe('createMainPageElements', () => {
    /**
     * Тест проверяет, что для диапазона страниц с 3 по 5 создаются элементы
     * для каждой страницы в этом диапазоне (3, 4, 5).
     *
     * Параметр currentPage=4 передается, но не используется в этой функции,
     * он нужен для других частей системы пагинации.
     *
     * Это основной диапазон отображаемых страниц в пагинации.
     */
    test('создает элементы для указанного диапазона страниц', () => {
      const result = createMainPageElements(3, 5, 4, '/blog/', mockCreateElement);

      expect(result).toHaveLength(3);
      expect(mockCreateElement).toHaveBeenCalledWith('page', 3);
      expect(mockCreateElement).toHaveBeenCalledWith('page', 4);
      expect(mockCreateElement).toHaveBeenCalledWith('page', 5);
      expect(mockCreateElement).toHaveBeenCalledTimes(3);
    });
  });

  /**
   * Тесты для функции createLastPageElements
   *
   * Функция создает многоточие и элемент последней страницы в конце пагинации
   * при необходимости (когда конечная страница основного диапазона < totalPages)
   */
  describe('createLastPageElements', () => {
    /**
     * Тест проверяет, что при endPage=5 и totalPages=10 создаются:
     * 1. Многоточие в конце (так как endPage < totalPages - 1)
     * 2. Элемент последней страницы (так как endPage < totalPages)
     *
     * Это соответствует ситуации, когда текущая страница находится в начале,
     * и нужно показать многоточие и ссылку на последнюю страницу после основного диапазона.
     */
    test('создает многоточие и последнюю страницу при необходимости', () => {
      const result = createLastPageElements(5, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(2);
      expect(mockCreateElement).toHaveBeenCalledWith('ellipsis-end');
      expect(mockCreateElement).toHaveBeenCalledWith('last-page');
      expect(mockCreateElement).toHaveBeenCalledTimes(2);
    });

    /**
     * Тест проверяет, что при endPage=10 и totalPages=10 не создаются никакие элементы,
     * так как последняя страница уже включена в основной диапазон страниц.
     *
     * Это соответствует ситуации, когда текущая страница близка к концу,
     * и последняя страница отображается в основном диапазоне.
     */
    test('не создает элементы, если endPage равен totalPages', () => {
      const result = createLastPageElements(10, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(0);
      expect(mockCreateElement).not.toHaveBeenCalled();
    });

    /**
     * Тест проверяет, что при endPage=9 и totalPages=10 создается только элемент
     * последней страницы, но не многоточие, так как между девятой и десятой страницами
     * нет промежутка.
     *
     * Это соответствует ситуации, когда текущая страница предпоследняя,
     * и последняя страница отображается отдельно, но без многоточия.
     */
    test('создает только последнюю страницу, если endPage равен totalPages - 1', () => {
      const result = createLastPageElements(9, 10, '/blog/', mockCreateElement);

      expect(result).toHaveLength(1);
      expect(mockCreateElement).toHaveBeenCalledWith('last-page');
      expect(mockCreateElement).toHaveBeenCalledTimes(1);
    });
  });
});
