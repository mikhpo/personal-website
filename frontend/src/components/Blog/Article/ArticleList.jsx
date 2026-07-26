import React, { useState, useEffect, useCallback } from 'react';
import { Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import { blogService } from '@services';

/**
 * Компонент списка статей блога.
 *
 * Загружает и отображает список статей из API блога с поддержкой пагинации.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.categorySlug] - Слаг категории для фильтрации (categories__slug)
 * @param {string} [props.seriesSlug] - Слаг серии для фильтрации (series__slug)
 * @param {string} [props.topicSlug] - Слаг темы для фильтрации (topics__slug)
 * @return {JSX.Element} Компонент списка статей
 *
 * @example
 * // Список всех статей
 * <ArticleList />
 *
 * @example
 * // Статьи категории
 * <ArticleList categorySlug="react" />
 */
const ArticleList = ({ categorySlug, seriesSlug, topicSlug }) => {
  /**
   * Состояние статей
   * @type {[Array, function]}
   */
  const [articles, setArticles] = useState([]);

  /**
   * Состояние загрузки данных
   * @type {[boolean, function]}
   */
  const [loading, setLoading] = useState(true);

  /**
   * Состояние ошибки при загрузке данных
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

  /**
   * Текущая страница пагинации
   * @type {[number, function]}
   */
  const [currentPage, setCurrentPage] = useState(1);

  /**
   * Общее количество страниц
   * @type {[number, function]}
   */
  const [totalPages, setTotalPages] = useState(1);

  /**
   * Наличие следующей страницы
   * @type {[boolean, function]}
   */
  const [hasNext, setHasNext] = useState(false);

  /**
   * Наличие предыдущей страницы
   * @type {[boolean, function]}
   */
  const [hasPrevious, setHasPrevious] = useState(false);

  /**
   * Счётчик повторных попыток загрузки
   * @type {[number, function]}
   */
  const [retryCount, setRetryCount] = useState(0);

  /**
   * Запрашивает статьи с фильтрами по слагам и указанной страницей.
   *
   * Слаги передаются как данные; пустые значения пропускаются при сборке URL
   * (blogService.getArticles использует buildApiUrl).
   *
   * @function fetchArticles
   * @param {number} page - Номер страницы для запроса
   * @return {Promise<Object>} Ответ API со списком статей
   */
  const fetchArticles = useCallback((page) => {
    return blogService.getArticles({
      categories__slug: categorySlug,
      series__slug: seriesSlug,
      topics__slug: topicSlug,
      page,
    });
  }, [categorySlug, seriesSlug, topicSlug]);

  /**
   * Эффект для загрузки статей при монтировании, изменении фильтра/страницы или повторной попытке
   */
  useEffect(() => {
    /**
     * Асинхронная функция для загрузки статей из API
     * @async
     * @function loadArticles
     * @return {Promise<void>}
     */
    const loadArticles = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchArticles(currentPage);
        const articlesList = data.results || data;
        setArticles(Array.isArray(articlesList) ? articlesList : []);
        if (data.count !== undefined) {
          const pageSize = articlesList.length || 10;
          setTotalPages(Math.ceil(data.count / pageSize));
          setHasNext(!!data.next);
          setHasPrevious(!!data.previous);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, [fetchArticles, currentPage, retryCount]);

  /**
   * Обработчик повторной попытки загрузки данных.
   *
   * Сбрасывает страницу на первую и инициирует повторный запрос через эффект.
   * @function handleRetry
   * @return {void}
   */
  const handleRetry = () => {
    setCurrentPage(1);
    setRetryCount((count) => count + 1);
  };

  // Отображение индикатора загрузки
  if (loading) {
    return <SpinnerComponent message="Загрузка статей..." />;
  }

  // Отображение сообщения об ошибке с кнопкой повтора
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
                onClick={handleRetry}
              >
                Повторить
              </Button>
            )
          }
        ]}
      />
    );
  }

  // Отображение сообщения о пустом списке статей
  if (articles.length === 0) {
    return <AlertList messages={[{ message: "Статьи не найдены", level: "info" }]} />;
  }

  // Отображение списка статей
  return (
    <div className="mb-3 pb-3">
      {articles.map(article => (
        <ArticleCard key={article.id} article={article} />
      ))}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        hasNext={hasNext}
        hasPrevious={hasPrevious}
        onPageChange={setCurrentPage}
        onNext={() => setCurrentPage(p => p + 1)}
        onPrevious={() => setCurrentPage(p => p - 1)}
        type="navigation"
      />
    </div>
  );
};

ArticleList.propTypes = {
  categorySlug: PropTypes.string,
  seriesSlug: PropTypes.string,
  topicSlug: PropTypes.string,
};

export default ArticleList;
