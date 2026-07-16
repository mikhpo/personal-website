import React, { useState, useEffect } from 'react';
import { Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';

/**
 * Компонент списка статей блога.
 *
 * Загружает и отображает список статей из API блога с поддержкой пагинации.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
 *
 * @component
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.apiUrl="/api/blog/articles/"] - URL API для загрузки статей
 * @return {JSX.Element} Компонент списка статей
 *
 * @example
 * // Использование с URL по умолчанию
 * <ArticleList />
 *
 * @example
 * // Использование с пользовательским URL
 * <ArticleList apiUrl="/api/blog/articles/?categories__slug=react" />
 */
const ArticleList = ({ apiUrl = '/api/blog/articles/' }) => {
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
   * Эффект для загрузки статей при монтировании компонента или изменении страницы/apiUrl
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
        const separator = apiUrl.includes('?') ? '&' : '?';
        const url = currentPage > 1 ? `${apiUrl}${separator}page=${currentPage}` : apiUrl;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        const data = await response.json();
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
  }, [apiUrl, currentPage]);

  /**
   * Обработчик повторной попытки загрузки данных
   * @function handleRetry
   * @return {void}
   */
  const handleRetry = () => {
    /**
     * Асинхронная функция для повторной загрузки статей из API
     * @async
     * @function retryLoadArticles
     * @return {Promise<void>}
     */
    const retryLoadArticles = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`);
        }
        const data = await response.json();
        const articlesList = data.results || data;
        setArticles(Array.isArray(articlesList) ? articlesList : []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    retryLoadArticles();
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
  apiUrl: PropTypes.string,
};

export default ArticleList;
