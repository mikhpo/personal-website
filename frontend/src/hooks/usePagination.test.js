/**
 * Тесты для хука usePagination.
 *
 * Проверяют управление состоянием пагинации,
 * вычисление следующей/предыдущей страниц и переходы.
 */

import { renderHook, act } from '@testing-library/react';
import usePagination from './usePagination';

describe('usePagination', () => {
  /**
   * Проверяет начальное состояние.
   */
  describe('начальное состояние', () => {
    test('устанавливает значения по умолчанию', () => {
      const { result } = renderHook(() => usePagination());

      expect(result.current.currentPage).toBe(1);
      expect(result.current.totalPages).toBe(1);
      expect(result.current.hasNext).toBe(false);
      expect(result.current.hasPrevious).toBe(false);
    });

    test('принимает начальный номер страницы', () => {
      const { result } = renderHook(() => usePagination({ initialPage: 5 }));

      expect(result.current.currentPage).toBe(5);
    });

    test('принимает общее количество страниц', () => {
      const { result } = renderHook(() => usePagination({ totalPages: 10 }));

      expect(result.current.totalPages).toBe(10);
    });
  });

  /**
   * Проверяет вычисление hasNext и hasPrevious.
   */
  describe('hasNext и hasPrevious', () => {
    test('hasNext=true когда currentPage < totalPages', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      expect(result.current.hasNext).toBe(true);
      expect(result.current.hasPrevious).toBe(false);
    });

    test('hasNext=false когда currentPage === totalPages', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 5, totalPages: 5 })
      );

      expect(result.current.hasNext).toBe(false);
    });

    test('hasPrevious=true когда currentPage > 1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 3, totalPages: 5 })
      );

      expect(result.current.hasPrevious).toBe(true);
    });

    test('hasPrevious=false когда currentPage === 1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      expect(result.current.hasPrevious).toBe(false);
    });

    test('оба false когда только одна страница', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 1 })
      );

      expect(result.current.hasNext).toBe(false);
      expect(result.current.hasPrevious).toBe(false);
    });
  });

  /**
   * Проверяет функцию nextPage.
   */
  describe('nextPage', () => {
    test('увеличивает currentPage на 1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      act(() => {
        result.current.nextPage();
      });

      expect(result.current.currentPage).toBe(2);
    });

    test('не увеличивает страницу когда hasNext=false', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 5, totalPages: 5 })
      );

      const currentPageBefore = result.current.currentPage;

      act(() => {
        result.current.nextPage();
      });

      // Страница не должна измениться
      expect(result.current.currentPage).toBe(currentPageBefore);
    });

    test('обновляет hasNext и hasPrevious после перехода', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      expect(result.current.hasPrevious).toBe(false);

      act(() => {
        result.current.nextPage();
      });

      expect(result.current.hasPrevious).toBe(true);
    });
  });

  /**
   * Проверяет функцию previousPage.
   */
  describe('previousPage', () => {
    test('уменьшает currentPage на 1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 3, totalPages: 5 })
      );

      act(() => {
        result.current.previousPage();
      });

      expect(result.current.currentPage).toBe(2);
    });

    test('не уменьшает страницу когда hasPrevious=false', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      const currentPageBefore = result.current.currentPage;

      act(() => {
        result.current.previousPage();
      });

      // Страница не должна измениться
      expect(result.current.currentPage).toBe(currentPageBefore);
    });
  });

  /**
   * Проверяет функцию goToPage.
   */
  describe('goToPage', () => {
    test('устанавливает указанную страницу', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 10 })
      );

      act(() => {
        result.current.goToPage(5);
      });

      expect(result.current.currentPage).toBe(5);
    });

    test('не позволяет перейти на страницу меньше 1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 3, totalPages: 5 })
      );

      const currentPageBefore = result.current.currentPage;

      act(() => {
        result.current.goToPage(0);
      });

      expect(result.current.currentPage).toBe(currentPageBefore);
    });

    test('не позволяет перейти на страницу больше totalPages', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 3, totalPages: 5 })
      );

      const currentPageBefore = result.current.currentPage;

      act(() => {
        result.current.goToPage(10);
      });

      expect(result.current.currentPage).toBe(currentPageBefore);
    });

    test('позволяет перейти на последнюю страницу', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      act(() => {
        result.current.goToPage(5);
      });

      expect(result.current.currentPage).toBe(5);
      expect(result.current.hasNext).toBe(false);
    });
  });

  /**
   * Проверяет функцию setTotalPages.
   */
  describe('setTotalPages', () => {
    test('обновляет общее количество страниц', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5 })
      );

      expect(result.current.totalPages).toBe(5);

      act(() => {
        result.current.setTotalPages(10);
      });

      expect(result.current.totalPages).toBe(10);
      expect(result.current.hasNext).toBe(true);
    });

    test('пересчитывает hasNext после обновления totalPages', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 5, totalPages: 5 })
      );

      expect(result.current.hasNext).toBe(false);

      act(() => {
        result.current.setTotalPages(10);
      });

      expect(result.current.hasNext).toBe(true);
    });

    test('пересчитывает hasPrevious при currentPage=1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 1 })
      );

      act(() => {
        result.current.setTotalPages(5);
      });

      // Переход на страницу 2 должен включить hasPrevious
      act(() => {
        result.current.nextPage();
      });

      expect(result.current.hasPrevious).toBe(true);
    });
  });

  /**
   * Проверяет callback onPageChange.
   */
  describe('onPageChange callback', () => {
    test('вызывает onPageChange при nextPage', () => {
      const onPageChange = jest.fn();
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5, onPageChange })
      );

      act(() => {
        result.current.nextPage();
      });

      expect(onPageChange).toHaveBeenCalledWith(2);
    });

    test('вызывает onPageChange при previousPage', () => {
      const onPageChange = jest.fn();
      const { result } = renderHook(() =>
        usePagination({ initialPage: 3, totalPages: 5, onPageChange })
      );

      act(() => {
        result.current.previousPage();
      });

      expect(onPageChange).toHaveBeenCalledWith(2);
    });

    test('вызывает onPageChange при goToPage', () => {
      const onPageChange = jest.fn();
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5, onPageChange })
      );

      act(() => {
        result.current.goToPage(4);
      });

      expect(onPageChange).toHaveBeenCalledWith(4);
    });

    test('не вызывает onPageChange для недопустимых страниц', () => {
      const onPageChange = jest.fn();
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 5, onPageChange })
      );

      act(() => {
        result.current.goToPage(0); // Недопустимо
      });

      expect(onPageChange).not.toHaveBeenCalled();

      act(() => {
        result.current.goToPage(10); // Недопустимо
      });

      expect(onPageChange).not.toHaveBeenCalled();
    });
  });

  /**
   * Проверяет граничные случаи.
   */
  describe('граничные случаи', () => {
    test('работает с totalPages=1', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 1 })
      );

      expect(result.current.currentPage).toBe(1);
      expect(result.current.totalPages).toBe(1);
      expect(result.current.hasNext).toBe(false);
      expect(result.current.hasPrevious).toBe(false);
    });

    test('работает с большим количеством страниц', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 1, totalPages: 1000 })
      );

      expect(result.current.hasNext).toBe(true);

      act(() => {
        result.current.goToPage(1000);
      });

      expect(result.current.hasNext).toBe(false);
      expect(result.current.hasPrevious).toBe(true);
    });

    test('corректно обрабатывает начальный номер страницы в середине диапазона', () => {
      const { result } = renderHook(() =>
        usePagination({ initialPage: 50, totalPages: 100 })
      );

      expect(result.current.currentPage).toBe(50);
      expect(result.current.hasNext).toBe(true);
      expect(result.current.hasPrevious).toBe(true);
    });
  });
});
