/**
 * Сервис для работы с API блога.
 *
 * Предоставляет методы для выполнения запросов к API блога:
 * - Получение списка статей
 * - Получение детальной информации о статье
 * - Создание комментариев
 * - Получение категорий, серий и тем
 */

import api from './api';
import { buildApiUrl } from '../utils/apiUrl';

/**
 * Базовый URL для API блога.
 * @type {string}
 */
const BASE_URL = '/api/blog';

/**
 * Сервис для работы с блогом.
 * @namespace
 */
export const blogService = {
  /**
   * Получает список статей.
   *
   * @async
   * @param {Object} [params={}] - Параметры запроса
   * @param {string} [params.page] - Номер страницы
   * @param {string} [params.categories__slug] - Фильтр по слагу категории
   * @param {string} [params.series__slug] - Фильтр по слагу серии
   * @param {string} [params.topics__slug] - Фильтр по слагу темы
   * @param {string} [params.search] - Поисковый запрос
   * @return {Promise<Object>} Объект со списком статей и пагинацией
   *
   * @example
   * // Получить все статьи
   * const data = await blogService.getArticles();
   *
   * @example
   * // Получить статьи из категории
   * const data = await blogService.getArticles({ categories__slug: 'react' });
   */
  async getArticles(params = {}) {
    return api.get(buildApiUrl(`${BASE_URL}/articles/`, params));
  },

  /**
   * Получает детальную информацию о статье.
   *
   * @async
   * @param {number|string} id - ID или слаг статьи
   * @return {Promise<Object>} Данные статьи
   *
   * @example
   * const article = await blogService.getArticle(1);
   */
  async getArticle(id) {
    return api.get(`${BASE_URL}/articles/${id}/`);
  },

  /**
   * Создает новый комментарий к статье.
   *
   * @async
   * @param {number} articleId - ID статьи
   * @param {Object} data - Данные комментария
   * @param {string} data.content - Содержимое комментария
   * @return {Promise<Object>} Созданный комментарий
   *
   * @example
   * const comment = await blogService.createComment(1, { content: 'Отличная статья!' });
   */
  async createComment(articleId, data) {
    return api.post(`${BASE_URL}/articles/${articleId}/comments/`, data);
  },

  /**
   * Получает список комментариев к статье.
   *
   * @async
   * @param {number} articleId - ID статьи
   * @return {Promise<Object>} Объект со списком комментариев
   *
   * @example
   * const comments = await blogService.getComments(1);
   */
  async getComments(articleId) {
    return api.get(`${BASE_URL}/articles/${articleId}/comments/`);
  },

  /**
   * Получает список категорий.
   *
   * @async
   * @return {Promise<Object>} Объект со списком категорий
   *
   * @example
   * const categories = await blogService.getCategories();
   */
  async getCategories() {
    return api.get(`${BASE_URL}/categories/`);
  },

  /**
   * Получает детальную информацию о категории.
   *
   * @async
   * @param {string} slug - Слаг категории
   * @return {Promise<Object>} Данные категории
   *
   * @example
   * const category = await blogService.getCategory('react');
   */
  async getCategory(slug) {
    return api.get(`${BASE_URL}/categories/${slug}/`);
  },

  /**
   * Получает список серий.
   *
   * @async
   * @return {Promise<Object>} Объект со списком серий
   *
   * @example
   * const series = await blogService.getSeries();
   */
  async getSeries() {
    return api.get(`${BASE_URL}/series/`);
  },

  /**
   * Получает детальную информацию о серии.
   *
   * @async
   * @param {string} slug - Слаг серии
   * @return {Promise<Object>} Данные серии
   *
   * @example
   * const series = await blogService.getSerie('django-best-practices');
   */
  async getSerie(slug) {
    return api.get(`${BASE_URL}/series/${slug}/`);
  },

  /**
   * Получает список тем.
   *
   * @async
   * @return {Promise<Object>} Объект со списком тем
   *
   * @example
   * const topics = await blogService.getTopics();
   */
  async getTopics() {
    return api.get(`${BASE_URL}/topics/`);
  },

  /**
   * Получает детальную информацию о теме.
   *
   * @async
   * @param {string} slug - Слаг темы
   * @return {Promise<Object>} Данные темы
   *
   * @example
   * const topic = await blogService.getTopic('frontend');
   */
  async getTopic(slug) {
    return api.get(`${BASE_URL}/topics/${slug}/`);
  },
};

export default blogService;
