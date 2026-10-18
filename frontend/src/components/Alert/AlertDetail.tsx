import React, { useEffect, useState } from 'react';
import { Alert as BSAlert } from 'react-bootstrap';

/** Уровень важности сообщения. */
export type AlertLevel = 'success' | 'info' | 'warning' | 'error' | 'danger';

/** Свойства компонента сообщения для пользователя. */
export interface AlertProps {
  /** Текст сообщения (может содержать HTML). */
  message: string;
  /** Уровень важности, определяет цветовую схему. */
  level: AlertLevel;
  /** Можно ли пользователю вручную закрыть сообщение. */
  dismissible?: boolean;
  /** Должно ли сообщение автоматически закрываться через заданное время. */
  autoClose?: boolean;
  /** Время в миллисекундах до автоматического закрытия. */
  autoCloseDelay?: number;
  /** Дополнительные действия под основным сообщением. */
  actions?: React.ReactNode;
}

/**
 * Компонент для отображения сообщений для пользователя.
 *
 * Отображает сообщение определенного уровня важности с возможностью
 * автоматического или ручного закрытия. Уровни error и danger отображаются
 * красным (danger), остальные - соответствующими цветами Bootstrap.
 *
 * При активации autoClose компонент автоматически скроет себя через указанное
 * время, при dismissible пользователь может закрыть сообщение вручную.
 *
 * @example
 * <Alert
 *   message="Операция выполнена успешно!"
 *   level="success"
 *   autoClose={true}
 *   autoCloseDelay={3000}
 * />
 */
const Alert = ({
  message,
  level,
  dismissible = true,
  autoClose = false,
  autoCloseDelay = 5000,
  actions,
}: AlertProps) => {
  const [show, setShow] = useState(true);

  useEffect(() => {
    if (autoClose && show) {
      const timer = setTimeout(() => {
        setShow(false);
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
    return undefined;
  }, [autoClose, autoCloseDelay, show]);

  if (!show) {
    return null;
  }

  const variantMap: Record<AlertLevel, string> = {
    success: 'success',
    info: 'info',
    warning: 'warning',
    error: 'danger',
    danger: 'danger',
  };

  const variant = variantMap[level] || 'info';

  return (
    <BSAlert variant={variant} onClose={dismissible ? () => setShow(false) : undefined} dismissible={dismissible}>
      <div dangerouslySetInnerHTML={{ __html: message }} />
      {actions && <div className="mt-2">{actions}</div>}
    </BSAlert>
  );
};

export default Alert;
