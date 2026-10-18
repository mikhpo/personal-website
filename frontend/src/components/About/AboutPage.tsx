import React, { useCallback, useEffect, useState } from 'react';
import Spinner from '@components/Spinner/Spinner';
import LoadingError from '@components/Alert/LoadingError';
import type { components } from '../../types/api-schema';

type AboutData = components['schemas']['About'];

/** Свойства компонента страницы "Обо мне". */
export interface AboutPageProps {
  /** Адрес API с содержимым страницы. */
  apiUrl?: string;
}

/**
 * Компонент страницы "Обо мне".
 *
 * Загружает содержимое страницы из API и отображает его как HTML.
 * Пустой контент не выводит ничего - на странице остается только заголовок.
 */
const About = ({ apiUrl = '/api/about/' }: AboutPageProps) => {
  // Состояния компонента: content - текст страницы, loading - идет загрузка, error - текст ошибки
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** Выполняет запрос к API и возвращает данные ответа. */
  const fetchRequest = useCallback(async (): Promise<AboutData> => {
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }

    return response.json();
  }, [apiUrl]);

  /** Загружает содержимое страницы при монтировании и по кнопке "Повторить". */
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchRequest();
      setContent(data.content || '');
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, [fetchRequest]);

  useEffect(() => {
    load();
  }, [load]);

  /** Повторяет загрузку содержимого страницы по кнопке "Повторить". */
  const handleRetry = () => {
    load();
  };

  if (loading) {
    return <Spinner message="Загрузка страницы..." />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={handleRetry} />;
  }

  if (!content) {
    return null;
  }

  // Контент редактируется владельцем сайта в админке, поэтому доверенный
  // HTML выводится как есть - так же отображается текст статей блога
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
};

export default About;
