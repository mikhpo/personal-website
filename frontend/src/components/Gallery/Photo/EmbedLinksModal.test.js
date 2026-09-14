import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EmbedLinksModal from './EmbedLinksModal';

/**
 * Набор тестов для компонента EmbedLinksModal.
 *
 * Проверяет формирование постоянных ссылок на превью для каждого
 * размера из готового набора и копирование ссылки в буфер обмена.
 */
describe('EmbedLinksModal', () => {
  const sizes = [400, 800, 1200, 1600];

  /**
   * Проверяет, что для каждого размера отображается неизменяемое поле
   * с постоянной ссылкой вида /gallery/embed/{photoId}/{size}.{ext}
   * с расширением формата исходного изображения и абсолютным адресом сайта.
   */
  test('рендерит ссылку для каждого размера', () => {
    render(<EmbedLinksModal photoId={7} sizes={sizes} ext="jpg" />);

    for (const size of sizes) {
      const input = screen.getByLabelText(`Ссылка на превью ${size} пикселов`);
      expect(input).toHaveValue(`http://localhost/gallery/embed/7/${size}.jpg`);
      expect(input).toHaveAttribute('readonly');
    }
  });

  /**
   * Проверяет, что расширение ссылки соответствует формату исходника.
   */
  test('использует расширение формата исходного изображения', () => {
    render(<EmbedLinksModal photoId={7} sizes={[800]} ext="png" />);

    const input = screen.getByLabelText('Ссылка на превью 800 пикселов');
    expect(input).toHaveValue('http://localhost/gallery/embed/7/800.png');
  });

  /**
   * Проверяет подписи размеров в пикселах по наибольшей стороне.
   */
  test('отображает подписи размеров в пикселах', () => {
    render(<EmbedLinksModal photoId={7} sizes={sizes} ext="jpg" />);

    expect(screen.getByText('400 px')).toBeInTheDocument();
    expect(screen.getByText('1600 px')).toBeInTheDocument();
  });

  /**
   * Проверяет копирование ссылки выбранного размера в буфер обмена.
   */
  test('копирует ссылку по нажатию кнопки', async () => {
    const user = userEvent.setup();
    render(<EmbedLinksModal photoId={7} sizes={[800]} ext="jpg" />);

    await user.click(screen.getByText('Копировать'));

    expect(await navigator.clipboard.readText()).toBe('http://localhost/gallery/embed/7/800.jpg');
    expect(await screen.findByText('Скопировано')).toBeInTheDocument();
  });

  /**
   * Проверяет, что подтверждение копирования исчезает через некоторое время.
   */
  test('возвращает подпись кнопки после подтверждения копирования', async () => {
    const user = userEvent.setup();
    render(<EmbedLinksModal photoId={7} sizes={[800]} ext="jpg" />);

    await user.click(screen.getByText('Копировать'));
    expect(await screen.findByText('Скопировано')).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText('Копировать')).toBeInTheDocument(), { timeout: 3000 });
  });
});
