/**
 * Сервис для работы с API блога.
 *
 * Предоставляет методы для выполнения запросов к API блога:
 * - Получение списка статей
 * - Получение детальной информации о статье
 * - Создание комментариев
 * - Получение категорий, серий и тем
 *
 * Типы ответов и параметров берутся из сгенерированной OpenAPI-схемы;
 * список статей возвращает пагинированный ответ, списки категорий,
 * серий и тем - готовые массивы без пагинации.
 */

import type { components, operations } from '@api-types/api-schema';
import type { Paginated } from '@api-types/pagination';
import api from './api';
import { buildApiUrl } from '../utils/apiUrl';

type Article = components['schemas']['Article'];
type Comment = components['schemas']['Comment'];
type Category = components['schemas']['Category'];
type Series = components['schemas']['Series'];
type Topic = components['schemas']['Topic'];

type ArticleListQuery = operations['blog_articles_list']['parameters']['query'];
type CategoryListQuery = operations['blog_categories_list']['parameters']['query'];
type SeriesListQuery = operations['blog_series_list']['parameters']['query'];
type TopicListQuery = operations['blog_topics_list']['parameters']['query'];

const BASE_URL = '/api/blog';

export const blogService = {
  /**
   * Получает список статей.
   *
   * @example
   * const data = await blogService.getArticles();
   *
   * @example
   * const data = await blogService.getArticles({ categories__slug: 'react' });
   */
  async getArticles(params: ArticleListQuery = {}): Promise<Paginated<Article>> {
    return api.get(buildApiUrl(`${BASE_URL}/articles/`, params));
  },

  /**
   * Получает детальную информацию о статье.
   *
   * @example
   * const article = await blogService.getArticle(1);
   */
  async getArticle(id: number): Promise<Article> {
    return api.get(`${BASE_URL}/articles/${id}/`);
  },

  /**
   * Создает статью из данных формы (multipart).
   *
   * @example
   * const formData = new FormData();
   * formData.append('title', 'Заголовок');
   * const article = await blogService.createArticle(formData);
   */
  async createArticle(formData: FormData): Promise<Article> {
    return api.postForm(`${BASE_URL}/articles/`, formData);
  },

  /**
   * Обновляет статью из данных формы (multipart).
   *
   * @example
   * const article = await blogService.updateArticle(1, formData);
   */
  async updateArticle(id: number, formData: FormData): Promise<Article> {
    return api.putForm(`${BASE_URL}/articles/${id}/`, formData);
  },

  /**
   * Создает новый комментарий к статье.
   *
   * @example
   * const comment = await blogService.createComment(1, { content: 'Отличная статья!' });
   */
  async createComment(articleId: number, data: { content: string; parent?: number | null }): Promise<Comment> {
    return api.post(`${BASE_URL}/comments/`, { article: articleId, ...data });
  },

  /**
   * Получает полный список категорий без пагинации.
   *
   * @example
   * const categories = await blogService.getCategories();
   */
  async getCategories(params: CategoryListQuery = {}): Promise<Category[]> {
    return api.get(buildApiUrl(`${BASE_URL}/categories/`, params));
  },

  /**
   * Получает полный список серий без пагинации.
   *
   * @example
   * const series = await blogService.getSeries();
   */
  async getSeries(params: SeriesListQuery = {}): Promise<Series[]> {
    return api.get(buildApiUrl(`${BASE_URL}/series/`, params));
  },

  /**
   * Получает полный список тем без пагинации.
   *
   * @example
   * const topics = await blogService.getTopics();
   */
  async getTopics(params: TopicListQuery = {}): Promise<Topic[]> {
    return api.get(buildApiUrl(`${BASE_URL}/topics/`, params));
  },
};

export default blogService;
