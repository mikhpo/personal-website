/**
 * Тесты для компонента ArticleForm.
 *
 * Проверяет создание и редактирование статей: загрузку справочников,
 * валидацию, публикацию и сохранение черновика, автосохранение
 * с проверкой изменений и переход в режим обновления после создания.
 */

import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import ArticleForm from './ArticleForm';
import { blogService, navigateTo } from '@services';

// Мок для blogService и navigateTo
jest.mock('@services');

// Мок для @tinymce/tinymce-react: TinyMCE использует iframe, который не работает в jsdom
jest.mock('@tinymce/tinymce-react', () => ({
  Editor: ({ value, onEditorChange, disabled }) => (
    <textarea
      aria-label="Содержание"
      value={value}
      onChange={(e) => onEditorChange(e.target.value)}
      disabled={disabled}
    />
  ),
}));

// Мок для компонента AlertList
jest.mock('@components/Alert/AlertList', () => {
  return function MockAlertList({ messages }) {
    return (
      <div data-testid="alert-list">
        {messages.map((msg) => (
          <div key={`${msg.level}-${msg.message}`} data-testid={`alert-${msg.level}`}>{msg.message}</div>
        ))}
      </div>
    );
  };
});

// Мок для компонента SpinnerComponent
jest.mock('@components/Spinner/Spinner', () => {
  return function MockSpinnerComponent({ message }) {
    return <div data-testid="spinner">{message}</div>;
  };
});

describe('ArticleForm', () => {
  const taxonomies = {
    categories: [{ id: 1, name: 'Разработка' }, { id: 2, name: 'Путешествия' }],
    series: [{ id: 3, name: 'Серия А' }],
    topics: [{ id: 4, name: 'Тема Б' }],
  };

  const createdArticle = { id: 10, url: '/blog/article/test/', slug: 'test' };

  /**
   * Рендерит форму и дожидается загрузки справочников
   * @param {Object} [props={}] - Пропсы компонента
   * @return {Promise<void>}
   */
  const renderForm = async (props = {}) => {
    render(<ArticleForm {...props} />);
    await act(async () => {});
  };

  /**
   * Заполняет обязательные поля формы
   * @param {string} [title='Новая статья'] - Заголовок
   * @param {string} [content='<p>Текст</p>'] - Контент
   * @return {void}
   */
  const fillRequiredFields = (title = 'Новая статья', content = '<p>Текст</p>') => {
    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: title } });
    fireEvent.change(screen.getByLabelText('Содержание'), { target: { value: content } });
  };

  /**
   * Продвигает фейковое время на интервал автосохранения
   * @return {Promise<void>}
   */
  const advanceAutosave = async () => {
    await act(async () => {
      await jest.advanceTimersByTimeAsync(60000);
    });
  };

  beforeAll(() => {
    jest.useFakeTimers();
  });

  beforeEach(() => {
    blogService.getCategories.mockResolvedValue({ results: taxonomies.categories });
    blogService.getSeries.mockResolvedValue({ results: taxonomies.series });
    blogService.getTopics.mockResolvedValue({ results: taxonomies.topics });
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'csrftoken=test-csrf-token-12345',
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
    jest.resetAllMocks();
    jest.useFakeTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  describe('создание статьи', () => {
    /**
     * Проверяет отображение всех полей и кнопок формы новой статьи.
     */
    test('отображает поля формы и кнопки сохранения', async () => {
      await renderForm();
      expect(screen.getByLabelText('Заголовок')).toBeInTheDocument();
      expect(screen.getByLabelText('Краткое описание')).toBeInTheDocument();
      expect(screen.getByLabelText('Содержание')).toBeInTheDocument();
      expect(screen.getByLabelText('Категории')).toBeInTheDocument();
      expect(screen.getByLabelText('Серии')).toBeInTheDocument();
      expect(screen.getByLabelText('Темы')).toBeInTheDocument();
      expect(screen.getByLabelText('Обложка')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /сохранить черновик/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /опубликовать/i })).toBeInTheDocument();
    });

    /**
     * Проверяет загрузку справочников и вывод их в селекторы.
     */
    test('загружает справочники в селекторы', async () => {
      await renderForm();
      expect(blogService.getCategories).toHaveBeenCalledTimes(1);
      expect(screen.getByText('Разработка')).toBeInTheDocument();
      expect(screen.getByText('Путешествия')).toBeInTheDocument();
      expect(screen.getByText('Серия А')).toBeInTheDocument();
      expect(screen.getByText('Тема Б')).toBeInTheDocument();
    });

    /**
     * Проверяет валидацию: публикация с пустым заголовком блокируется.
     */
    test('блокирует публикацию с пустым заголовком', async () => {
      await renderForm();
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      expect(screen.getByTestId('alert-error')).toHaveTextContent('Заполните заголовок статьи');
      expect(blogService.createArticle).not.toHaveBeenCalled();
    });

    /**
     * Проверяет валидацию: публикация с пустым текстом блокируется.
     */
    test('блокирует публикацию с пустым текстом', async () => {
      await renderForm();
      fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Только заголовок' } });
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      expect(screen.getByTestId('alert-error')).toHaveTextContent('Заполните текст статьи');
      expect(blogService.createArticle).not.toHaveBeenCalled();
    });

    /**
     * Проверяет публикацию: FormData содержит public=true и выполняется переход на статью.
     */
    test('публикует статью и выполняет переход на её страницу', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      expect(blogService.createArticle).toHaveBeenCalledTimes(1);
      const formData = blogService.createArticle.mock.calls[0][0];
      expect(formData.get('title')).toBe('Новая статья');
      expect(formData.get('content')).toBe('<p>Текст</p>');
      expect(formData.get('public')).toBe('true');
      expect(navigateTo).toHaveBeenCalledWith('/blog/article/test/');
    });

    /**
     * Проверяет сохранение черновика: FormData содержит public=false.
     */
    test('сохраняет черновик', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      fireEvent.click(screen.getByRole('button', { name: /сохранить черновик/i }));
      await act(async () => {});
      const formData = blogService.createArticle.mock.calls[0][0];
      expect(formData.get('public')).toBe('false');
      expect(navigateTo).toHaveBeenCalledWith('/blog/article/test/');
    });

    /**
     * Проверяет выбор категорий: выбранные идентификаторы уходят на сервер.
     */
    test('отправляет выбранные категории', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      const select = screen.getByLabelText('Категории');
      Array.from(select.options).forEach((option) => {
        option.selected = option.value === '1' || option.value === '2';
      });
      fireEvent.change(select);
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      const formData = blogService.createArticle.mock.calls[0][0];
      expect(formData.getAll('categories')).toEqual(['1', '2']);
    });

    /**
     * Проверяет отправку пустого маркера для незаполненных связей.
     */
    test('отправляет пустой маркер для пустых связей', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      const formData = blogService.createArticle.mock.calls[0][0];
      expect(formData.get('categories')).toBe('');
      expect(formData.get('series')).toBe('');
      expect(formData.get('topics')).toBe('');
    });

    /**
     * Проверяет отображение ошибки при неудачном сохранении.
     */
    test('отображает ошибку при неудачном сохранении', async () => {
      blogService.createArticle.mockRejectedValue(new Error('Ошибка сети'));
      await renderForm();
      fillRequiredFields();
      fireEvent.click(screen.getByRole('button', { name: /опубликовать/i }));
      await act(async () => {});
      expect(screen.getByTestId('alert-error')).toHaveTextContent('Ошибка сети');
      expect(navigateTo).not.toHaveBeenCalled();
    });
  });

  describe('редактирование статьи', () => {
    const existingArticle = {
      id: 5,
      title: 'Существующая статья',
      description: 'Описание статьи',
      content: '<p>Существующий текст</p>',
      public: true,
      categories: [{ id: 1, name: 'Разработка' }],
      series: [],
      topics: [],
      image: '/media/blog/articles/cover.jpg',
      url: '/blog/article/existing/',
    };

    beforeEach(() => {
      blogService.getArticle.mockResolvedValue(existingArticle);
    });

    /**
     * Проверяет загрузку данных статьи в форму при редактировании.
     */
    test('загружает данные статьи', async () => {
      await renderForm({ articleId: 5 });
      expect(blogService.getArticle).toHaveBeenCalledWith(5);
      expect(screen.getByDisplayValue('Существующая статья')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Описание статьи')).toBeInTheDocument();
      expect(screen.getByLabelText('Содержание')).toHaveValue('<p>Существующий текст</p>');
    });

    /**
     * Проверяет, что сохранение опубликованной статьи не меняет статус.
     */
    test('сохраняет опубликованную статью кнопкой «Сохранить»', async () => {
      blogService.updateArticle.mockResolvedValue(existingArticle);
      await renderForm({ articleId: 5 });
      expect(screen.getByRole('button', { name: 'Сохранить' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Снять с публикации' })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'Опубликовать' })).not.toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Сохранить' })).toHaveClass('btn-dark');
      expect(screen.getByRole('button', { name: 'Снять с публикации' })).toHaveClass('btn-outline-dark');
      fireEvent.click(screen.getByRole('button', { name: 'Сохранить' }));
      await act(async () => {});
      expect(blogService.updateArticle).toHaveBeenCalledTimes(1);
      const [id, formData] = blogService.updateArticle.mock.calls[0];
      expect(id).toBe(5);
      expect(formData.get('public')).toBe('true');
      expect(navigateTo).toHaveBeenCalledWith('/blog/article/existing/');
    });

    /**
     * Проверяет снятие статьи с публикации соответствующей кнопкой.
     */
    test('снимает статью с публикации кнопкой «Снять с публикации»', async () => {
      blogService.updateArticle.mockResolvedValue(existingArticle);
      await renderForm({ articleId: 5 });
      fireEvent.click(screen.getByRole('button', { name: 'Снять с публикации' }));
      await act(async () => {});
      const formData = blogService.updateArticle.mock.calls[0][1];
      expect(formData.get('public')).toBe('false');
    });

    /**
     * Проверяет, что у статьи-черновика остаются кнопки черновика.
     */
    test('у черновика отображаются кнопки черновика', async () => {
      blogService.getArticle.mockResolvedValue({ ...existingArticle, public: false });
      await renderForm({ articleId: 5 });
      expect(screen.getByRole('button', { name: 'Сохранить черновик' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Опубликовать' })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'Снять с публикации' })).not.toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Сохранить черновик' })).toHaveClass('btn-dark');
      expect(screen.getByRole('button', { name: 'Опубликовать' })).toHaveClass('btn-outline-dark');
    });

    /**
     * Проверяет порядок кнопок: сохранение в текущем статусе слева, смена статуса справа.
     */
    test('у опубликованной статьи «Сохранить» слева от «Снять с публикации»', async () => {
      await renderForm({ articleId: 5 });
      const save = screen.getByRole('button', { name: 'Сохранить' });
      const unpublish = screen.getByRole('button', { name: 'Снять с публикации' });
      expect(save.compareDocumentPosition(unpublish) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    });

    /**
     * Проверяет порядок кнопок черновика: сохранение слева, публикация справа.
     */
    test('у черновика «Сохранить черновик» слева от «Опубликовать»', async () => {
      blogService.getArticle.mockResolvedValue({ ...existingArticle, public: false });
      await renderForm({ articleId: 5 });
      const draft = screen.getByRole('button', { name: 'Сохранить черновик' });
      const publish = screen.getByRole('button', { name: 'Опубликовать' });
      expect(draft.compareDocumentPosition(publish) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    });

    /**
     * Проверяет показ текущей обложки и управление флагом удаления.
     */
    test('показывает текущую обложку и флаг удаления', async () => {
      await renderForm({ articleId: 5 });
      expect(screen.getByAltText('Текущая обложка')).toBeInTheDocument();
      fireEvent.click(screen.getByLabelText('Убрать обложку'));
      blogService.updateArticle.mockResolvedValue(existingArticle);
      fireEvent.click(screen.getByRole('button', { name: 'Сохранить' }));
      await act(async () => {});
      const formData = blogService.updateArticle.mock.calls[0][1];
      expect(formData.get('remove_image')).toBe('true');
    });
  });

  describe('автосохранение', () => {
    /**
     * Проверяет, что по истечении интервала при заполненной форме создается черновик.
     */
    test('создает черновик по истечении интервала', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      await advanceAutosave();
      expect(blogService.createArticle).toHaveBeenCalledTimes(1);
      const formData = blogService.createArticle.mock.calls[0][0];
      expect(formData.get('public')).toBe('false');
      expect(navigateTo).not.toHaveBeenCalled();
      expect(screen.getByText(/Автосохранено в \d{2}:\d{2}/)).toBeInTheDocument();
    });

    /**
     * Проверяет, что при отсутствии изменений повторный тик не отправляет запрос.
     */
    test('не отправляет запрос при отсутствии изменений', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      await advanceAutosave();
      await advanceAutosave();
      expect(blogService.createArticle).toHaveBeenCalledTimes(1);
    });

    /**
     * Проверяет, что пустая по заголовку форма не автосохраняется.
     */
    test('не сохраняет форму без заголовка', async () => {
      await renderForm();
      fireEvent.change(screen.getByLabelText('Содержание'), { target: { value: '<p>Текст</p>' } });
      await advanceAutosave();
      expect(blogService.createArticle).not.toHaveBeenCalled();
    });

    /**
     * Проверяет переход в режим обновления после автосохранения черновика.
     */
    test('обновляет статью после её автосоздания', async () => {
      blogService.createArticle.mockResolvedValue(createdArticle);
      await renderForm();
      fillRequiredFields();
      await advanceAutosave();
      fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Обновленный заголовок' } });
      await advanceAutosave();
      expect(blogService.updateArticle).toHaveBeenCalledTimes(1);
      const [id, formData] = blogService.updateArticle.mock.calls[0];
      expect(id).toBe(10);
      expect(formData.get('title')).toBe('Обновленный заголовок');
      expect(blogService.createArticle).toHaveBeenCalledTimes(1);
    });

    /**
     * Проверяет, что при редактировании без изменений автосохранение не срабатывает.
     */
    test('не автосохраняет неизмененную статью', async () => {
      blogService.getArticle.mockResolvedValue({
        id: 5,
        title: 'Существующая статья',
        description: '',
        content: '<p>Текст</p>',
        public: false,
        categories: [],
        series: [],
        topics: [],
        url: '/blog/article/existing/',
      });
      await renderForm({ articleId: 5 });
      await advanceAutosave();
      expect(blogService.updateArticle).not.toHaveBeenCalled();
    });

    /**
     * Проверяет, что изменения черновика при редактировании автосохраняются.
     */
    test('автосохраняет изменения черновика', async () => {
      blogService.getArticle.mockResolvedValue({
        id: 5,
        title: 'Черновик статьи',
        description: '',
        content: '<p>Текст</p>',
        public: false,
        categories: [],
        series: [],
        topics: [],
        url: '/blog/article/existing/',
      });
      blogService.updateArticle.mockResolvedValue({ id: 5, url: '/blog/article/existing/' });
      await renderForm({ articleId: 5 });
      fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Правка черновика' } });
      await advanceAutosave();
      expect(blogService.updateArticle).toHaveBeenCalledTimes(1);
      const formData = blogService.updateArticle.mock.calls[0][1];
      expect(formData.get('public')).toBe('false');
    });

    /**
     * Проверяет, что опубликованная статья автосохранением не обновляется:
     * изменения сохраняются только явной кнопкой «Сохранить».
     */
    test('не автосохраняет опубликованную статью', async () => {
      blogService.getArticle.mockResolvedValue({
        id: 5,
        title: 'Опубликованная статья',
        description: '',
        content: '<p>Текст</p>',
        public: true,
        categories: [],
        series: [],
        topics: [],
        url: '/blog/article/existing/',
      });
      await renderForm({ articleId: 5 });
      fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Правки без сохранения' } });
      await advanceAutosave();
      expect(blogService.updateArticle).not.toHaveBeenCalled();
      expect(screen.queryByText(/Автосохранено в/)).not.toBeInTheDocument();
    });

    /**
     * Проверяет индикацию ошибки автосохранения.
     */
    test('показывает предупреждение при ошибке автосохранения', async () => {
      blogService.createArticle.mockRejectedValue(new Error('Ошибка сети'));
      await renderForm();
      fillRequiredFields();
      await advanceAutosave();
      expect(screen.getByText('Не удалось автосохранить')).toBeInTheDocument();
      expect(navigateTo).not.toHaveBeenCalled();
    });

    /**
     * Проверяет повтор автосохранения после ошибки при следующем тике.
     */
    test('повторяет автосохранение после ошибки', async () => {
      blogService.createArticle
        .mockRejectedValueOnce(new Error('Ошибка сети'))
        .mockResolvedValueOnce(createdArticle);
      await renderForm();
      fillRequiredFields();
      await advanceAutosave();
      expect(screen.getByText('Не удалось автосохранить')).toBeInTheDocument();
      await advanceAutosave();
      expect(blogService.createArticle).toHaveBeenCalledTimes(2);
      expect(screen.getByText(/Автосохранено в \d{2}:\d{2}/)).toBeInTheDocument();
    });
  });
});
