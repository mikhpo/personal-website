import React, { useCallback } from 'react';
import Spinner from '@components/Spinner/Spinner';
import LoadingError from '@components/Alert/LoadingError';
import { aboutService } from '@services';
import { useApiData } from '@hooks';

/**
 * Компонент страницы "Обо мне".
 *
 * Загружает содержимое страницы из API и отображает его как HTML.
 * Пустой контент не выводит ничего - на странице остается только заголовок.
 */
const About = () => {
  const loadAbout = useCallback(() => aboutService.getAbout(), []);
  const { data, loading, error, refetch } = useApiData(loadAbout);

  /** Повторяет загрузку содержимого страницы по кнопке "Повторить". */
  const handleRetry = () => {
    refetch();
  };

  const content = data?.content ?? '';

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
