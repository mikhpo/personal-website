import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { Container, Row, Col } from "react-bootstrap";
import { Button } from "react-bootstrap";
import Spinner from "@components/Spinner/Spinner";
import AlertList from "@components/Alert/AlertList";
import AlbumCard from "@components/Gallery/Album/AlbumCard";
import usePagination from "@hooks/usePagination";
import Pagination from "@components/Pagination/Pagination";

/**
 * Компонент списка альбомов с пагинацией.
 *
 * Загружает и отображает список альбомов из API. Обрабатывает различные состояния:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.apiUrl="/api/gallery/albums/"] - URL для получения списка альбомов
 * @return {JSX.Element} Компонент списка альбомов
 *
 * @example
 * // Использование с URL по умолчанию
 * <AlbumList />
 *
 * @example
 * // Использование с кастомным URL
 * <AlbumList apiUrl="/api/custom/albums/" />
 *
 * @description
 * Компонент выполняет следующие функции:
 * 1. Загружает данные альбомов через fetch API с пагинацией
 * 2. Обрабатывает состояния загрузки, ошибки и пустого списка
 * 3. Отображает альбомы в виде сетки карточек
 * 4. Предоставляет возможность повторной загрузки при ошибке
 * 5. Поддерживает пагинацию с навигацией по страницам
 */
const AlbumList = ({ apiUrl = "/api/gallery/albums/" }) => {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    currentPage,
    totalPages,
    hasNext,
    hasPrevious,
    nextPage,
    previousPage,
    goToPage,
    setTotalPages,
  } = usePagination({ initialPage: 1 });

  const fetchAlbums = useCallback(
    (page = 1) => {
      // eslint-disable-next-line react-x/set-state-in-effect
      setLoading(true);
      // eslint-disable-next-line react-x/set-state-in-effect
      setError(null);

    const url = new URL(apiUrl, window.location.origin);
    url.searchParams.append("page", page);
    url.searchParams.append("page_size", "20");

    fetch(url.toString())
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const albumsList = data.results || data;
        setAlbums(Array.isArray(albumsList) ? albumsList : []);
        if (data.count) {
          const pageSize = data.results ? data.results.length : albumsList.length;
          setTotalPages(Math.ceil(data.count / (pageSize || 20)));
        }

        setLoading(false);
      })
      .catch((err) => {
        // eslint-disable-next-line react-x/set-state-in-effect
        setError(err.message);
        // eslint-disable-next-line react-x/set-state-in-effect
        setLoading(false);
      });
    },
    [apiUrl, setTotalPages],
  );

  useEffect(() => {
    fetchAlbums(currentPage);
  }, [currentPage, fetchAlbums]);

  const handleRetry = () => {
    fetchAlbums(currentPage);
  };

  const handlePageChange = (page) => {
    goToPage(page);
  };

  if (loading) {
    return <Spinner message="Загрузка альбомов..." />;
  }

  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: "error",
            actions: (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={handleRetry}
                data-testid="retry-button"
              >
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  if (albums.length === 0) {
    return (
      <AlertList
        messages={[{ message: "Нет доступных альбомов", level: "info" }]}
      />
    );
  }

  return (
    <Container data-testid="album-list-container">
      <Row xs={1} md={4} className="g-4 justify-content-center">
        {albums.map((album) => (
          <Col key={album.id}>
            <AlbumCard album={album} />
          </Col>
        ))}
      </Row>
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          hasNext={hasNext}
          hasPrevious={hasPrevious}
          onNext={nextPage}
          onPrevious={previousPage}
          onPageChange={handlePageChange}
          type="navigation"
        />
      )}
    </Container>
  );
};

AlbumList.propTypes = {
  apiUrl: PropTypes.string,
};

export default AlbumList;
