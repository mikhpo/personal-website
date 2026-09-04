/**
 * Тесты для компонента SearchForm.
 *
 * Проверяет рендер поля с начальным значением и подсказкой, а также
 * формирование URL перехода при отправке формы: с запросом и без него.
 * Переход подменяется моком утилиты navigateTo (jsdom не реализует навигацию).
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchForm from './SearchForm';
import { navigateTo } from '../../utils/navigate';

jest.mock('../../utils/navigate');

describe('SearchForm', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверяет рендер поля с начальным значением поискового запроса.
   * Начальное значение пропа search должно попадать в поле ввода.
   */
  test('отображает поле с начальным значением запроса', () => {
    render(<SearchForm targetUrl="/blog/" search="react" />);

    expect(screen.getByDisplayValue('react')).toBeInTheDocument();
  });

  /**
   * Проверяет подстановку значений по умолчанию: подсказку в поле
   * и текст кнопки отправки.
   */
  test('отображает подсказку и текст кнопки по умолчанию', () => {
    render(<SearchForm targetUrl="/blog/" />);

    expect(screen.getByPlaceholderText('Поиск...')).toBeInTheDocument();
    expect(screen.getByText('Найти')).toBeInTheDocument();
  });

  /**
   * Проверяет переход на targetUrl с query-параметром search при отправке
   * непустого запроса. Запрос кодируется для URL.
   */
  test('отправляет запрос на targetUrl с параметром search', () => {
    const { container } = render(<SearchForm targetUrl="/blog/" />);

    fireEvent.change(screen.getByPlaceholderText('Поиск...'), {
      target: { value: 'react js' },
    });
    fireEvent.submit(container.querySelector('form'));

    expect(navigateTo).toHaveBeenCalledWith('/blog/?search=react%20js');
  });

  /**
   * Проверяет обрезку пробелов по краям запроса перед формированием URL.
   */
  test('обрезает пробелы в запросе', () => {
    const { container } = render(<SearchForm targetUrl="/blog/" />);

    fireEvent.change(screen.getByPlaceholderText('Поиск...'), {
      target: { value: '  react  ' },
    });
    fireEvent.submit(container.querySelector('form'));

    expect(navigateTo).toHaveBeenCalledWith('/blog/?search=react');
  });

  /**
   * Проверяет сброс поиска: пустой запрос ведет на targetUrl
   * без query-параметра.
   */
  test('пустой запрос ведет на targetUrl без параметра', () => {
    const { container } = render(<SearchForm targetUrl="/blog/" />);

    fireEvent.change(screen.getByPlaceholderText('Поиск...'), {
      target: { value: '   ' },
    });
    fireEvent.submit(container.querySelector('form'));

    expect(navigateTo).toHaveBeenCalledWith('/blog/');
  });

  /**
   * Проверяет использование нестандартных текстов пропсов placeholder
   * и submitLabel.
   */
  test('отображает пользовательские подсказку и текст кнопки', () => {
    render(<SearchForm targetUrl="/search/" placeholder="Поиск по сайту..." submitLabel="Искать" />);

    expect(screen.getByPlaceholderText('Поиск по сайту...')).toBeInTheDocument();
    expect(screen.getByText('Искать')).toBeInTheDocument();
  });
});
