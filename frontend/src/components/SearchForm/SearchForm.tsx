import React, { useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import { navigateTo } from '@services';

/** Свойства формы поиска. */
export interface SearchFormProps {
  /** URL страницы результатов, куда выполняется переход при отправке. */
  targetUrl: string;
  /** Начальное значение поискового запроса (текущий запрос для уточнения). */
  search?: string;
  /** Подсказка в поле ввода. */
  placeholder?: string;
  /** Текст кнопки отправки. */
  submitLabel?: string;
  /** Вариант Bootstrap кнопки отправки. */
  buttonVariant?: string;
}

/**
 * Универсальная форма поиска.
 *
 * Отображает поле ввода и кнопку отправки. При отправке выполняет переход
 * на страницу результатов с query-параметром search, поэтому один и тот же
 * компонент используется любым разделом сайта (блог, галерея, общий поиск).
 * Пустой запрос ведет на targetUrl без параметра, что сбрасывает поиск.
 *
 * @example
 * <SearchForm targetUrl="/blog/" placeholder="Поиск по статьям..." />
 */
const SearchForm = ({
  targetUrl,
  search = '',
  placeholder = 'Поиск...',
  submitLabel = 'Найти',
  buttonVariant = 'outline-secondary',
}: SearchFormProps) => {
  /** Текущее значение поискового запроса. */
  const [query, setQuery] = useState(search);

  /**
   * Переводит пользователя на targetUrl с query-параметром search;
   * пустой или состоящий из пробелов запрос ведет на targetUrl без параметра.
   */
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmedQuery = query.trim();
    navigateTo(trimmedQuery ? `${targetUrl}?search=${encodeURIComponent(trimmedQuery)}` : targetUrl);
  };

  return (
    <Form className="d-flex" role="search" onSubmit={handleSubmit}>
      <Form.Control
        type="search"
        className="me-2"
        placeholder={placeholder}
        aria-label={placeholder}
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <Button variant={buttonVariant} type="submit">
        {submitLabel}
      </Button>
    </Form>
  );
};

export default SearchForm;
