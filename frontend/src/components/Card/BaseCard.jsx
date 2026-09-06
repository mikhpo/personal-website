import React from 'react';
import { Card } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Базовый компонент карточки с изображением.
 *
 * Универсальный компонент карточки для отображения объектов с изображением,
 * названием и описанием. Поддерживает различные варианты отображения и
 * может быть использован для категорий, серий, альбомов и других сущностей.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} props.title - Заголовок карточки
 * @param {string} props.url - URL для перехода при клике
 * @param {string} [props.image] - URL изображения (опционально)
 * @param {string} [props.description] - Описание (опционально)
 * @param {string} [props.imageAlt] - Alt текст для изображения
 * @param {string} [props.variant="centered"] - Вариант отображения ("centered" | "left")
 * @param {string} [props.className] - Дополнительные CSS классы
 * @param {Object} [props.cardImgProps] - Дополнительные пропсы для Card.Img
 * @return {JSX.Element} Компонент карточки
 *
 * @example
 * // Базовое использование с изображением
 * <BaseCard
 *   title="Разработка"
 *   url="/blog/category/razrabotka/"
 *   image="/media/blog/categories/dev.jpg"
 *   description="Статьи о разработке"
 * />
 *
 * @example
 * // Использование без изображения
 * <BaseCard
 *   title="Альбом без обложки"
 *   url="/gallery/album/1/"
 * />
 */
const BaseCard = ({
  title,
  url,
  image,
  description,
  imageAlt,
  variant = 'centered',
  className = '',
  cardImgProps = {},
}) => {
  const isCentered = variant === 'centered';
  const cardClassName = `shadow bg-white rounded ${isCentered ? 'text-center' : ''} h-100 ${className}`;

  return (
    <Card className={cardClassName}>
      {image && (
        <a href={url}>
          <Card.Img
            variant="top"
            src={image}
            alt={imageAlt || title}
            loading="lazy"
            {...cardImgProps}
          />
        </a>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title as="h3" className={`fs-5 ${isCentered ? 'mt-auto' : ''}`}>
          <a href={url} className="text-dark">
            {title}
          </a>
        </Card.Title>
        {description && (
          <Card.Text>{description}</Card.Text>
        )}
      </Card.Body>
    </Card>
  );
};

BaseCard.propTypes = {
  title: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired,
  image: PropTypes.string,
  description: PropTypes.string,
  imageAlt: PropTypes.string,
  variant: PropTypes.oneOf(['centered', 'left']),
  className: PropTypes.string,
  cardImgProps: PropTypes.object,
};

export default BaseCard;
