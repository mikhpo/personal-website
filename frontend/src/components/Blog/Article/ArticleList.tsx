import React, { useCallback } from 'react';
import { Card } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import Pagination from '@components/Pagination/Pagination';
import { countHtmlWords, truncateHtmlWords } from '@components/Blog/utils/html';
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
 * Каждая статья выводится карточкой с заголовком и превью содержимого в виде
 * HTML: фотографии и форматирование статьи видны прямо в списке. При длинном
 * содержимом (более 200 слов) превью обрезается до 50 слов с добавлением
 * ссылки "Читать дальше". Обрабатывает состояния загрузки, ошибки и пустого
 * списка, предоставляет возможность повторной попытки загрузки при ошибке.
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
    return <LoadingError message={error} onRetry={handleRetry} />;
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
      {articles.map((article) => {
        const articleUrl = article.url || `/blog/${article.id}/`;

        // Порог длины считается по сырому HTML: словом считается любая группа
        // символов между пробелами, включая атрибуты тегов
        const isLong = countHtmlWords(article.content) > 200;

        // Обрезка не разрывает теги: закрывает открытые элементы и сохраняет
        // фотографии, встретившиеся до точки обрезки
        const preview = isLong ? truncateHtmlWords(article.content, 50) : article.content;

        return (
          <div key={article.id} className="container mb-3 pb-3">
            <Card className="shadow mb-4 rounded justify-content">
              <Card.Body>
                <h2 className="card-title fs-4">
                  <a href={articleUrl}>{article.title}</a>
                </h2>
                <div className="card-text" dangerouslySetInnerHTML={{ __html: preview }} />
                {isLong && <a href={articleUrl}>Читать дальше</a>}
              </Card.Body>
            </Card>
          </div>
        );
      })}
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
