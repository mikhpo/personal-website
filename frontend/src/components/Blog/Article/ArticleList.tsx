import React, { useCallback, useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import { blogService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../../types/api-schema';

type Article = components['schemas']['Article'];

/** Свойства компонента списка статей. */
export interface ArticleListProps {
  /** Слаг категории для фильтрации (categories__slug). */
  categorySlug?: string;
  /** Слаг серии для фильтрации (series__slug). */
  seriesSlug?: string;
  /** Слаг темы для фильтрации (topics__slug). */
  topicSlug?: string;
  /** Поисковый запрос для фильтрации (search). */
  search?: string;
}

/**
 * Компонент списка статей блога.
 *
 * Загружает и отображает список статей из API блога с поддержкой пагинации.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
 *
 * @example
 * <ArticleList categorySlug="react" />
 *
 * @example
 * <ArticleList search="django" />
 */
const ArticleList = ({ categorySlug, seriesSlug, topicSlug, search }: ArticleListProps) => {
  /** Состояние статей. */
  const [articles, setArticles] = useState<Article[]>([]);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(true);

  /** Состояние ошибки при загрузке данных. */
  const [error, setError] = useState<string | null>(null);

  /** Текущая страница пагинации. */
  const [currentPage, setCurrentPage] = useState(1);

  /** Общее количество страниц. */
  const [totalPages, setTotalPages] = useState(1);

  /** Наличие следующей страницы. */
  const [hasNext, setHasNext] = useState(false);

  /** Наличие предыдущей страницы. */
  const [hasPrevious, setHasPrevious] = useState(false);

  /** Счётчик повторных попыток загрузки. */
  const [retryCount, setRetryCount] = useState(0);

  /**
   * Запрашивает статьи с фильтрами по слагам, поисковым запросом и указанной
   * страницей. Слаги и запрос передаются как данные; пустые значения
   * пропускаются при сборке URL (blogService.getArticles использует buildApiUrl).
   */
  const fetchArticles = useCallback(
    (page: number) => {
      return blogService.getArticles({
        categories__slug: categorySlug,
        series__slug: seriesSlug,
        topics__slug: topicSlug,
        search,
        page,
      });
    },
    [categorySlug, seriesSlug, topicSlug, search],
  );

  // Эффект для загрузки статей при монтировании, изменении фильтра/страницы или повторной попытке
  useEffect(() => {
    /** Загружает статьи из API. */
    const loadArticles = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchArticles(currentPage);
        const { items, totalPages, next, previous } = parseListResponse(data);
        setArticles(items);
        setTotalPages(totalPages);
        setHasNext(!!next);
        setHasPrevious(!!previous);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, [fetchArticles, currentPage, retryCount]);

  /**
   * Сбрасывает страницу на первую и инициирует повторный запрос через эффект.
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
              <Button variant="outline-primary" size="sm" onClick={handleRetry}>
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  // Отображение сообщения о пустом списке статей;
  // при активном поиске сообщение включает запрос пользователя
  if (articles.length === 0) {
    const emptyMessage = search ? `По запросу "${search}" ничего не найдено` : 'Статьи не найдены';
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  // Отображение списка статей
  return (
    <div className="mb-3 pb-3">
      {articles.map((article) => (
        <ArticleCard key={article.id} article={article} />
      ))}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        hasNext={hasNext}
        hasPrevious={hasPrevious}
        onPageChange={setCurrentPage}
        onNext={() => setCurrentPage((p) => p + 1)}
        onPrevious={() => setCurrentPage((p) => p - 1)}
        type="navigation"
      />
    </div>
  );
};

export default ArticleList;
