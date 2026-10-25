import React, { useCallback } from 'react';
import { Button } from 'react-bootstrap';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import { blogService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { searchEmptyMessage } from '@utils/messages';
import { useApiData, usePagination } from '@hooks';

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
  const { currentPage, totalPages, hasNext, hasPrevious, nextPage, previousPage, goToPage, setTotalPages } =
    usePagination({ initialPage: 1 });

  /**
   * Запрашивает статьи с фильтрами по слагам, поисковым запросом и текущей
   * страницей. Слаги и запрос передаются как данные; пустые значения
   * пропускаются при сборке URL (blogService.getArticles использует buildApiUrl).
   */
  const fetchArticles = useCallback(async () => {
    const data = await blogService.getArticles({
      categories__slug: categorySlug,
      series__slug: seriesSlug,
      topics__slug: topicSlug,
      search,
      page: currentPage,
    });
    const parsed = parseListResponse(data);
    setTotalPages(parsed.totalPages);
    return parsed.items;
  }, [categorySlug, seriesSlug, topicSlug, search, currentPage, setTotalPages]);

  const { data, loading, error, refetch } = useApiData(fetchArticles);
  const articles = data ?? [];

  /** Повторяет загрузку: на страницах дальше первой сбрасывает на первую. */
  const handleRetry = () => {
    if (currentPage !== 1) {
      goToPage(1);
    } else {
      refetch();
    }
  };

  // Отображение индикатора загрузки
  if (loading) {
    return <Spinner message="Загрузка статей..." />;
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
    const emptyMessage = searchEmptyMessage(search, 'Статьи не найдены');
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
        onPageChange={goToPage}
        onNext={nextPage}
        onPrevious={previousPage}
        type="navigation"
      />
    </div>
  );
};

export default ArticleList;
