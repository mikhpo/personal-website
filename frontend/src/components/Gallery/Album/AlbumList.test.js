/**
 * Тесты для компонента AlbumList.
 *
 * Проверяет корректность отображения списка альбомов с различными состояниями:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 * Тесты используют моки для изоляции компонента от внешних зависимостей.
 */

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AlbumList from "@components/Gallery/Album/AlbumList";

// Мокировать компонент AlbumCard для изоляции тестов
jest.mock("./AlbumCard", () => ({
  __esModule: true,
  default: ({ album }) => (
    <div data-testid={`album-card-${album.id}`}>{album.name}</div>
  ),
}));

// Мокировать компоненты Spinner и AlertList
jest.mock("@components/Spinner/Spinner", () => ({
  __esModule: true,
  default: ({ message }) => <p>{message}</p>,
}));

jest.mock("@components/Alert/AlertList", () => ({
  __esModule: true,
  default: ({ messages }) => (
    <div>
      {messages.map((msg) => (
        <div key={`${msg.level}-${msg.message}`} data-testid={`alert-${msg.level}`}>
          {msg.message}
          {msg.actions}
        </div>
      ))}
    </div>
  ),
}));

jest.mock("@hooks/usePagination", () => ({
  __esModule: true,
  default: () => ({
    currentPage: 1,
    totalPages: 1,
    hasNext: false,
    hasPrevious: false,
    nextPage: jest.fn(),
    previousPage: jest.fn(),
    goToPage: jest.fn(),
    setTotalPages: jest.fn(),
  }),
}));

jest.mock("@components/Pagination/Pagination", () => ({
  __esModule: true,
  default: () => null,
}));

describe("AlbumList", () => {
  // Тестовые данные альбомов
  const mockAlbums = [
    {
      id: 1,
      name: "Альбом 1",
      slug: "album-1",
      description: "Описание альбома 1",
      cover_thumbnail_url: "/media/album1.jpg",
    },
    {
      id: 2,
      name: "Альбом 2",
      slug: "album-2",
      description: "Описание альбома 2",
      cover_thumbnail_url: "/media/album2.jpg",
    },
    {
      id: 3,
      name: "Альбом 3",
      slug: "album-3",
    },
  ];

  // Настройка мока fetch перед каждым тестом
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ results: [] }),
      }),
    );
  });

  // Восстановление оригинального fetch после каждого теста
  afterEach(() => {
    jest.restoreAllMocks();
  });

  // Очистить моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверить отображение состояния загрузки.
   * Когда компонент загружает данные, должен отображаться компонент загрузки.
   */
  test("отображает состояние загрузки", () => {
    // Мокаем fetch чтобы он не завершался сразу
    global.fetch.mockImplementation(() => new Promise(() => {}));

    render(<AlbumList />);
    // Проверяем видимый текст (не visually-hidden)
    const visibleText = screen.getByText("Загрузка альбомов...", {
      selector: "p",
    });
    expect(visibleText).toBeInTheDocument();
  });

  /**
   * Проверить отображение состояния ошибки.
   * Когда возникает ошибка загрузки, должен отображаться компонент ошибки.
   */
  test("отображает состояние ошибки", async () => {
    // Мокаем сетевую ошибку
    global.fetch.mockRejectedValueOnce(new Error("Network error"));

    render(<AlbumList />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });

    // Проверить, что кнопка повтора отображается
    const retryButton = screen.getByText("Повторить");
    expect(retryButton).toBeInTheDocument();

    // Проверить, что кнопка повтора вызывает повторную загрузку
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    userEvent.click(retryButton);

    // Ждем завершения повторной загрузки
    await waitFor(() => {
      expect(screen.getByTestId("album-list-container")).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение пустого состояния.
   * Когда API возвращает пустой массив альбомов без ошибок,
   * должен отображаться компонент пустого состояния.
   */
  test("отображает пустое состояние", async () => {
    // Настроить мок API для возврата пустого списка
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<AlbumList />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByText("Нет доступных альбомов")).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение списка альбомов.
   * Когда API возвращает массив альбомов, должен отображаться список карточек.
   */
  test("отображает список альбомов", async () => {
    // Настроить мок API для возврата списка альбомов
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<AlbumList />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByTestId("album-list-container")).toBeInTheDocument();
    });

    // Проверить, что каждый альбом отображается
    mockAlbums.forEach((album) => {
      expect(screen.getByTestId(`album-card-${album.id}`)).toBeInTheDocument();
      expect(screen.getByText(album.name)).toBeInTheDocument();
    });
  });

  /**
   * Проверить передачу кастомного URL в API.
   * Компонент должен использовать полученный apiUrl для загрузки данных.
   */
  test("передает правильный apiUrl в fetch", async () => {
    const customApiUrl = "/custom/api/albums/";
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<AlbumList apiUrl={customApiUrl} />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("http://localhost/custom/api/albums/?page=1&page_size=20");
    });
  });

  /**
   * Проверить использование дефолтного URL если не передан.
   * Если apiUrl не передан, должен использоваться URL по умолчанию.
   */
  test("использует дефолтный apiUrl если не указан", async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<AlbumList />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("http://localhost/api/gallery/albums/?page=1&page_size=20");
    });
  });

  /**
   * Проверить правильную структуру сетки.
   * Компонент должен использовать правильные CSS классы для сетки Bootstrap.
   */
  test("использует правильную структуру сетки Bootstrap", async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    const renderResult = render(<AlbumList />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByTestId("album-list-container")).toBeInTheDocument();
    });

    // Проверить наличие контейнера
    const container = renderResult.container.querySelector(".container");
    expect(container).toBeInTheDocument();
    expect(container).toHaveAttribute("data-testid", "album-list-container");

    // Проверить наличие строки
    const row = renderResult.container.querySelector(".row");
    expect(row).toBeInTheDocument();
    expect(row).toHaveClass("g-4", "justify-content-center");

    // Проверить колонки (должны быть с правильными классами для responsive grid)
    const cols = renderResult.container.querySelectorAll(".col");
    expect(cols).toHaveLength(mockAlbums.length);

    // Проверить классы колонок (xs=1, md=4)
    cols.forEach((col) => {
      expect(col).toHaveClass("col"); // Базовый класс col
    });
  });

  /**
   * Проверить обработку ответа без поля results.
   * Компонент должен корректно обрабатывать прямой массив альбомов.
   */
  test("обрабатывает результат без results", async () => {
    // Мокаем ответ без поля results
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlbums,
    });

    render(<AlbumList />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByTestId("album-list-container")).toBeInTheDocument();
    });

    // Проверить, что альбомы отображаются
    mockAlbums.forEach((album) => {
      expect(screen.getByTestId(`album-card-${album.id}`)).toBeInTheDocument();
      expect(screen.getByText(album.name)).toBeInTheDocument();
    });
  });

  /**
   * Проверить обработку HTTP ошибок.
   * При получении ошибочного HTTP статуса должна устанавливаться ошибка.
   */
  test("обрабатывает HTTP ошибку", async () => {
    // Мокаем HTTP ошибку
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<AlbumList />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByText("Ошибка загрузки: 500")).toBeInTheDocument();
    });
  });
});
