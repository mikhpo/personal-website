import React from 'react';
import { Card } from 'react-bootstrap';

/** Свойства базовой карточки. */
export interface BaseCardProps {
  /** Заголовок карточки. */
  title: string;
  /** URL для перехода при клике. */
  url: string;
  /** URL изображения. */
  image?: string;
  /** Описание. */
  description?: string;
  /** Alt текст для изображения. */
  imageAlt?: string;
  /** Вариант отображения. */
  variant?: 'centered' | 'left';
  /** Дополнительные CSS классы. */
  className?: string;
  /** Дополнительные CSS классы заголовка. */
  titleClassName?: string;
  /** Разрешено ли проявление карточки. */
  revealed?: boolean;
  /** Дополнительные пропсы для Card.Img. */
  cardImgProps?: React.ComponentProps<typeof Card.Img>;
}

/**
 * Базовый компонент карточки с изображением.
 *
 * Универсальный компонент карточки для отображения объектов с изображением,
 * названием и описанием. Поддерживает различные варианты отображения и
 * может быть использован для категорий, серий, альбомов и других сущностей.
 *
 * Проп revealed управляет плавным проявлением карточки: masonry-сетка
 * разрешает проявление только после пересчета, учитывающего высоту изображения,
 * поэтому снимки не наваливаются друг на друга в начале загрузки. Без пропа
 * карточка видима сразу.
 *
 * @example
 * <BaseCard
 *   title="Разработка"
 *   url="/blog/category/razrabotka/"
 *   image="/media/blog/categories/dev.jpg"
 *   description="Статьи о разработке"
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
  titleClassName = '',
  revealed = true,
  cardImgProps = {},
}: BaseCardProps) => {
  const isCentered = variant === 'centered';
  const cardClassName = `shadow rounded ${isCentered ? 'text-center' : ''} h-100 ${className}`;

  const entranceClass = `card-entrance ${revealed || !image ? 'is-visible' : ''}`;

  return (
    <Card className={`${cardClassName} ${entranceClass}`}>
      {image && (
        <a href={url}>
          <Card.Img variant="top" src={image} alt={imageAlt || title} loading="lazy" {...cardImgProps} />
        </a>
      )}
      <Card.Body className="d-flex flex-column">
        <Card.Title as="h3" className={`fs-5 ${isCentered ? 'mt-auto' : ''} ${titleClassName}`}>
          <a href={url} className="text-decoration-none text-body">
            {title}
          </a>
        </Card.Title>
        {description && (
          <Card.Text>
            {/* Описание кликабельно, как и название, но без подчеркивания - карточка не должна выглядеть как набор ссылок */}
            <a href={url} className="text-decoration-none text-body">
              {description}
            </a>
          </Card.Text>
        )}
      </Card.Body>
    </Card>
  );
};

export default BaseCard;
