import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Form } from 'react-bootstrap';
import { navigateTo } from '../../utils/navigate';

/**
 * Универсальная форма поиска.
 *
 * Отображает поле ввода и кнопку отправки. При отправке выполняет переход
 * на страницу результатов с query-параметром search, поэтому один и тот же
 * компонент используется любым разделом сайта (блог, галерея, общий поиск).
 * Пустой запрос ведет на targetUrl без параметра, что сбрасывает поиск.
 *
 * @component
 * @param {Object} props - Свойства компонента
 * @param {string} props.targetUrl - URL страницы результатов, куда выполняется переход при отправке
 * @param {string} [props.search] - Начальное значение поискового запроса (текущий запрос для уточнения)
 * @param {string} [props.placeholder] - Подсказка в поле ввода
 * @param {string} [props.submitLabel] - Текст кнопки отправки
 * @param {string} [props.buttonVariant] - Вариант Bootstrap кнопки отправки (по умолчанию outline-secondary)
 * @return {JSX.Element} Элемент формы поиска
 *
 * @example
 * // Форма на странице блога
 * <SearchForm targetUrl="/blog/" placeholder="Поиск по статьям..." />
 *
 * @example
 * // Форма с текущим запросом и нестандартной кнопкой
 * <SearchForm targetUrl="/gallery/photos/" search="закат" submitLabel="Искать" />
 */
const SearchForm = ({ targetUrl, search, placeholder, submitLabel, buttonVariant }) => {
  /**
   * Текущее значение поискового запроса
   * @type {[string, function]}
   */
  const [query, setQuery] = useState(search);

  /**
   * Обработчик отправки формы.
   *
   * Переводит пользователя на targetUrl с query-параметром search;
   * пустой или состоящий из пробелов запрос ведет на targetUrl без параметра.
   *
   * @function handleSubmit
   * @param {React.FormEvent} event - Событие отправки формы
   * @return {void}
   */
  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmedQuery = query.trim();
    navigateTo(
      trimmedQuery
        ? `${targetUrl}?search=${encodeURIComponent(trimmedQuery)}`
        : targetUrl,
    );
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

SearchForm.propTypes = {
  targetUrl: PropTypes.string.isRequired,
  search: PropTypes.string,
  placeholder: PropTypes.string,
  submitLabel: PropTypes.string,
  buttonVariant: PropTypes.string,
};

SearchForm.defaultProps = {
  search: '',
  placeholder: 'Поиск...',
  submitLabel: 'Найти',
  buttonVariant: 'outline-secondary',
};

export default SearchForm;
