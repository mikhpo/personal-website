import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Container, Row, Col } from "react-bootstrap";
import { Button } from "react-bootstrap";
import Spinner from "@components/Spinner/Spinner";
import AlertList from "@components/Alert/AlertList";
import AlbumCard from "@components/Gallery/Album/AlbumCard";

/**
 * Компонент списка альбомов.
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
 * 1. Загружает данные альбомов через fetch API
 * 2. Обрабатывает состояния загрузки, ошибки и пустого списка
 * 3. Отображает альбомы в виде сетки карточек
 * 4. Предоставляет возможность повторной загрузки при ошибке
 */
const AlbumList = ({ apiUrl = "/api/gallery/albums/" }) => {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlbums = () => {
    setLoading(true);
    setError(null);

    fetch(apiUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const albumsList = data.results || data;
        setAlbums(Array.isArray(albumsList) ? albumsList : []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAlbums();
  }, [apiUrl]);

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
                onClick={fetchAlbums}
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
    </Container>
  );
};

AlbumList.propTypes = {
  apiUrl: PropTypes.string,
};

export default AlbumList;
