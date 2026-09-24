import React, { useState, useEffect, useCallback } from 'react';
import Spinner from '@components/Spinner/Spinner';
import LoadingError from '@components/Alert/LoadingError';

/**
 * Компонент страницы "Обо мне".
 *
 * Загружает содержимое страницы из API и отображает его как HTML.
 * Пустой контент не выводит ничего - на странице остается только заголовок.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.apiUrl='/api/about/'] - Адрес API с содержимым страницы
 * @return {JSX.Element|null} Компонент страницы либо null для пустого контента
 */
const About = ({ apiUrl = '/api/about/' }) => {
  // Состояния компонента: content - текст страницы, loading - идет загрузка, error - текст ошибки
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Выполняет запрос к API и возвращает данные ответа.
   *
   * Обернута в useCallback, чтобы стабильная ссылка на функцию не перезапускала useEffect.
   *
   * @return {Promise<Object>} Данные ответа в формате JSON
   * @throws {Error} При неуспешном статусе ответа
   */
  const fetchRequest = useCallback(async () => {
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }

    return response.json();
  }, [apiUrl]);

  /**
   * Загружает содержимое страницы из API и обновляет состояние компонента.
   *
   * Вызывается при монтировании компонента и по кнопке "Повторить".
   *
   * @return {Promise<void>}
   */
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

  /**
   * Повторяет загрузку содержимого страницы по кнопке "Повторить".
   */
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
