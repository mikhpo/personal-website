import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Компонент со списком постоянных ссылок на превью фотографии.
 *
 * Для каждого размера из готового набора формирует постоянную ссылку
 * вида /gallery/embed/{photoId}/{size}.{ext} и позволяет скопировать ее
 * в буфер обмена для вставки в редактор статей или сторонний ресурс.
 * Размер указан по наибольшей стороне, пропорции фотографии сохраняются,
 * превью отдается в формате исходного изображения.
 *
 * @component
 * @param {Object} props - Свойства компонента
 * @param {number} props.photoId - ID фотографии
 * @param {number[]} props.sizes - Набор размеров превью в пикселах по наибольшей стороне
 * @param {string} props.ext - Расширение файла исходного изображения
 * @return {JSX.Element} Список ссылок с кнопками копирования
 */
const EmbedLinksModal = ({ photoId, sizes, ext }) => {
  const [copiedSize, setCopiedSize] = useState(null);

  const buildEmbedUrl = (size) => `${window.location.origin}/gallery/embed/${photoId}/${size}.${ext}`;

  const copyEmbedUrl = async (size) => {
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

EmbedLinksModal.propTypes = {
  photoId: PropTypes.number.isRequired,
  sizes: PropTypes.arrayOf(PropTypes.number).isRequired,
  ext: PropTypes.string.isRequired,
};

export default EmbedLinksModal;
