import { buildApiUrl } from "./apiUrl";

/**
 * Тесты утилиты построения URL API-запросов.
 *
 * Проверяют сборку относительного URL из базового URL и параметров:
 * отсутствие параметров, добавление фильтров, пропуск пустых значений
 * и сохранение параметров, уже присутствующих в базовом URL.
 */
describe("buildApiUrl", () => {
  /**
   * Без параметров возвращается базовый URL без query-string.
   */
  test("возвращает базовый URL без параметров", () => {
    expect(buildApiUrl("/api/gallery/photos/")).toBe("/api/gallery/photos/");
  });

  /**
   * Параметры добавляются в query-string в порядке передачи.
   */
  test("добавляет параметры в query-string", () => {
    expect(
      buildApiUrl("/api/gallery/albums/", { tags__slug: "example-tag", page: 1 }),
    ).toBe("/api/gallery/albums/?tags__slug=example-tag&page=1");
  });

  /**
   * Пустые значения (undefined, null, "") не попадают в query-string.
   */
  test("пропускает пустые значения параметров", () => {
    expect(
      buildApiUrl("/api/gallery/photos/", {
        tags__slug: undefined,
        album: null,
        page: "",
      }),
    ).toBe("/api/gallery/photos/");
  });

  /**
   * Параметры, уже присутствующие в базовом URL, сохраняются, новые добавляются.
   */
  test("сохраняет параметры базового URL", () => {
    expect(
      buildApiUrl("/api/gallery/albums/?tag=nature", { page: 2 }),
    ).toBe("/api/gallery/albums/?tag=nature&page=2");
  });
});
