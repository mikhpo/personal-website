import React from 'react';
import { render, screen } from '@testing-library/react';
import PhotoNavigation from './PhotoNavigation';

/**
 * Тесты для компонента PhotoNavigation.
 *
 * Проверяет корректность отображения кнопок навигации между фотографиями,
 * правильность формирования ссылок и поведение при различных значениях пропсов.
 */
describe('PhotoNavigation', () => {
  const previousPhoto = { slug: 'previous-photo' };
  const nextPhoto = { slug: 'next-photo' };

  /**
   * Проверяет, что компонент возвращает null, когда обе фотографии равны null.
   * Это необходимо для корректного поведения на первой и последней фотографии альбома,
   * где одна из кнопок навигации должна отсутствовать.
   */
  test('возвращает null если обе фотографии null', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={null} nextPhoto={null} />
    );
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что компонент возвращает null, когда обе фотографии равны undefined.
   * Это дополнительная проверка для случая, когда пропсы могут быть не определены.
   */
  test('возвращает null если обе фотографии undefined', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={undefined} nextPhoto={undefined} />
    );
    expect(container.firstChild).toBeNull();
  });

  /**
   * Проверяет, что отображаются обе кнопки навигации, когда доступны обе фотографии.
   * Это стандартный случай для фотографий в середине альбома.
   */
  test('рендерит обе кнопки если обе фотографии есть', () => {
    render(<PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />);
    expect(screen.getByText('← Предыдущая')).toBeInTheDocument();
    expect(screen.getByText('Следующая ->')).toBeInTheDocument();
  });

  /**
   * Проверяет, что отображается только кнопка "Предыдущая", когда следующая фотография отсутствует.
   * Это случай для последней фотографии в альбоме.
   */
  test('рендерит только кнопку "Предыдущая" если nextPhoto null', () => {
    render(<PhotoNavigation previousPhoto={previousPhoto} nextPhoto={null} />);
    expect(screen.getByText('← Предыдущая')).toBeInTheDocument();
    expect(screen.queryByText('Следующая ->')).not.toBeInTheDocument();
  });

  /**
   * Проверяет, что отображается только кнопка "Следующая", когда предыдущая фотография отсутствует.
   * Это случай для первой фотографии в альбоме.
   */
  test('рендерит только кнопку "Следующая" если previousPhoto null', () => {
    render(<PhotoNavigation previousPhoto={null} nextPhoto={nextPhoto} />);
    expect(screen.queryByText('← Предыдущая')).not.toBeInTheDocument();
    expect(screen.getByText('Следующая ->')).toBeInTheDocument();
  });

  /**
   * Проверяет, что кнопка "Предыдущая" имеет правильную ссылку на фотографию.
   * Ссылка должна вести на страницу предыдущей фотографии в галерее по адресу /gallery/photo/{slug}/.
   */
  test('кнопка "Предыдущая" имеет правильную ссылку', () => {
    render(<PhotoNavigation previousPhoto={previousPhoto} nextPhoto={null} />);
    const button = screen.getByText('← Предыдущая');
    expect(button).toHaveAttribute('href', '/gallery/photo/previous-photo/');
  });

  /**
   * Проверяет, что кнопка "Следующая" имеет правильную ссылку на фотографию.
   * Ссылка должна вести на страницу следующей фотографии в галерее по адресу /gallery/photo/{slug}/.
   */
  test('кнопка "Следующая" имеет правильную ссылку', () => {
    render(<PhotoNavigation previousPhoto={null} nextPhoto={nextPhoto} />);
    const button = screen.getByText('Следующая ->');
    expect(button).toHaveAttribute('href', '/gallery/photo/next-photo/');
  });

  /**
   * Проверяет, что обе кнопки имеют вариант "primary".
   * Это необходимо для единообразия оформления кнопок навигации.
   */
  test('обе кнопки имеют вариант "primary"', () => {
    render(<PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveClass('btn-primary');
    });
  });

  /**
   * Проверяет, что контейнер использует flexbox с правильным выравниванием.
   * Это необходимо для корректного расположения кнопок по краям контейнера.
   */
  test('контейнер использует flexbox с правильным выравниванием', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />
    );
    const navigationContainer = container.firstChild;
    expect(navigationContainer).toHaveClass('d-flex', 'justify-content-between', 'mt-3');
  });

  /**
   * Проверяет, что кнопки обёрнуты в div контейнеры.
   * Это необходимо для правильной структуры разметки и последующей стилизации.
   */
  test('кнопки обёрнуты в div контейнеры', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />
    );
    const divs = container.querySelectorAll('.d-flex > div');
    expect(divs).toHaveLength(2);
  });

  /**
   * Проверяет, что компонент корректно рендерит навигацию с различными слагами.
   * Это проверка на корректную работу с разными значениями слагов фотографий.
   */
  test('рендерит с различными slug', () => {
    const prev = { slug: 'photo-1' };
    const next = { slug: 'photo-2' };
    render(<PhotoNavigation previousPhoto={prev} nextPhoto={next} />);
    const prevButton = screen.getByText('← Предыдущая');
    const nextButton = screen.getByText('Следующая ->');
    expect(prevButton).toHaveAttribute('href', '/gallery/photo/photo-1/');
    expect(nextButton).toHaveAttribute('href', '/gallery/photo/photo-2/');
  });

  /**
   * Проверяет, что кнопки навигации являются ссылками.
   * Это необходимо для возможности перехода между фотографиями.
   */
  test('кнопки являются ссылками', () => {
    render(<PhotoNavigation previousPhoto={previousPhoto} nextPhoto={nextPhoto} />);
    const links = screen.getAllByRole('button');
    expect(links).toHaveLength(2);
  });

  /**
   * Проверяет, что левый контейнер пустой, если нет предыдущей фотографии.
   * Это необходимо для корректного отображения только кнопки "Следующая".
   */
  test('левый контейнер пустой если нет previousPhoto', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={null} nextPhoto={nextPhoto} />
    );
    const leftContainer = container.querySelector('.d-flex > div:first-child');
    expect(leftContainer).toBeEmptyDOMElement();
  });

  /**
   * Проверяет, что правый контейнер пустой, если нет следующей фотографии.
   * Это необходимо для корректного отображения только кнопки "Предыдущая".
   */
  test('правый контейнер пустой если нет nextPhoto', () => {
    const { container } = render(
      <PhotoNavigation previousPhoto={previousPhoto} nextPhoto={null} />
    );
    const rightContainer = container.querySelector('.d-flex > div:last-child');
    expect(rightContainer).toBeEmptyDOMElement();
  });
});
