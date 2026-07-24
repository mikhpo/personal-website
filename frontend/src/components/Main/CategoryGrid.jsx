import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { Button } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import CategoryCard from '@components/Main/CategoryCard';

/**
 * Компонент сетки категорий блога.
 *
 * Загружает и отображает список категорий из API. Обрабатывает различные состояния:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 *
 * @return {JSX.Element} Компонент сетки категорий
 *
 * @example
 * // Использование компонента
 * <CategoryGrid />
 *
 * @description
 * Компонент выполняет следующие функции:
 * 1. Загружает данные категорий через fetch API
 * 2. Фильтрует категории с изображениями
 * 3. Обрабатывает состояния загрузки, ошибки и пустого списка
 * 4. Отображает категории в виде сетки карточек
 * 5. Предоставляет возможность повторной загрузки при ошибке
 */

// URL для получения списка категорий
const CATEGORIES_API_URL = '/api/blog/categories/';

const CategoryGrid = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCategories = useCallback(() => {
    const updateLoadingState = () => {
      // eslint-disable-next-line react-x/set-state-in-effect
      setLoading(true);
      // eslint-disable-next-line react-x/set-state-in-effect
      setError(null);
    };
    updateLoadingState();

    fetch(CATEGORIES_API_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const categoriesList = data.results || data;
        const withImages = (Array.isArray(categoriesList) ? categoriesList : [])
          .filter((cat) => cat.image);
        setCategories(withImages);
        setLoading(false);
      })
      .catch((err) => {
        // eslint-disable-next-line react-x/set-state-in-effect
        setError(err.message);
        // eslint-disable-next-line react-x/set-state-in-effect
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  if (loading) {
    return <Spinner message="Загрузка категорий..." />;
  }

  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: 'error',
            actions: (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={fetchCategories}
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

  if (categories.length === 0) {
    return (
      <AlertList
        messages={[{ message: 'Нет доступных категорий', level: 'info' }]}
      />
    );
  }

  return (
    <Container data-testid="category-grid-container">
      <h4>
        <p className="text-center">Выберите категорию</p>
      </h4>
      <Row
        xs={1} // 1 колонка на мобильных устройствах
        md={3} // 3 колонки на планшетах и десктопах (>=768px)
        className="g-4 justify-content-center"
      >
        {categories.map((category) => (
          <Col key={category.id}>
            <CategoryCard category={category} />
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default CategoryGrid;
