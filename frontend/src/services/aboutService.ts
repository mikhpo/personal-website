/**
 * Сервис для работы с API страницы "Обо мне".
 */

import type { components } from '@api-types/api-schema';
import api from './api';

type About = components['schemas']['About'];

const BASE_URL = '/api/about/';

export const aboutService = {
  /**
   * Получает содержимое страницы "Обо мне".
   *
   * @example
   * const about = await aboutService.getAbout();
   */
  async getAbout(): Promise<About> {
    return api.get(BASE_URL);
  },
};

export default aboutService;
