import React, { useState } from 'react';

/** Свойства компонента постоянных ссылок на превью. */
export interface EmbedLinksModalProps {
  /** ID фотографии. */
  photoId: number;
  /** Набор размеров превью в пикселах по наибольшей стороне. */
  sizes: number[];
  /** Расширение файла исходного изображения. */
  ext: string;
}

/**
 * Компонент со списком постоянных ссылок на превью фотографии.
 *
 * Для каждого размера из готового набора формирует постоянную ссылку
 * вида /gallery/embed/{photoId}/{size}.{ext} и позволяет скопировать ее
 * в буфер обмена для вставки в редактор статей или сторонний ресурс.
 * Размер указан по наибольшей стороне, пропорции фотографии сохраняются,
 * превью отдается в формате исходного изображения.
 */
const EmbedLinksModal = ({ photoId, sizes, ext }: EmbedLinksModalProps) => {
  const [copiedSize, setCopiedSize] = useState<number | null>(null);

  const buildEmbedUrl = (size: number): string => `${window.location.origin}/gallery/embed/${photoId}/${size}.${ext}`;

  const copyEmbedUrl = async (size: number) => {
    await navigator.clipboard.writeText(buildEmbedUrl(size));
    setCopiedSize(size);
    setTimeout(() => setCopiedSize((current) => (current === size ? null : current)), 2000);
  };

  return (
    <>
      <p className="mb-2">
        Постоянная ссылка на превью выбранного размера. Размер указан в пикселах по наибольшей стороне, пропорции
        фотографии сохраняются. Вставьте ссылку в обычное поле адреса изображения в редакторе.
      </p>
      {sizes.map((size) => (
        <div className="input-group mb-2" key={size}>
          <span className="input-group-text">{`${size} px`}</span>
          <input
            type="text"
            className="form-control"
            id={`embed-link-${size}`}
            aria-label={`Ссылка на превью ${size} пикселов`}
            value={buildEmbedUrl(size)}
            readOnly
            onFocus={(event) => event.target.select()}
          />
          <button type="button" className="btn btn-outline-dark" onClick={() => copyEmbedUrl(size)}>
            {copiedSize === size ? 'Скопировано' : 'Копировать'}
          </button>
        </div>
      ))}
    </>
  );
};

export default EmbedLinksModal;
