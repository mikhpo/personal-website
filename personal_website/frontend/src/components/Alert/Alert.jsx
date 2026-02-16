import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Alert as BSAlert } from 'react-bootstrap';

/**
 * Компонент для отображения сообщений для пользователя.
 *
 * Отображает сообщение определенного уровня важности с возможностью
 * автоматического или ручного закрытия. Поддерживает различные уровни
 * важности сообщений: успех, информация, предупреждение, ошибка.
 *
 * @component
 * @example
 * // Пример использования компонента с автоматическим закрытием
 * <Alert
 *   message="Операция выполнена успешно!"
 *   level="success"
 *   autoClose={true}
 *   autoCloseDelay={3000}
 * />
 *
 * @example
 * // Пример использования компонента с ручным закрытием
 * <Alert
 *   message="Произошла ошибка при загрузке данных"
 *   level="error"
 *   dismissible={true}
 * />
 *
 * @param {Object} props - Свойства компонента
 * @param {string} props.message - Текст сообщения (может содержать HTML), который будет отображен пользователю
 * @param {('success'|'info'|'warning'|'error'|'danger')} props.level - Уровень важности сообщения, определяет цветовую схему отображения
 * @param {boolean} [props.dismissible=true] - Флаг, указывающий, можно ли пользователю вручную закрыть сообщение
 * @param {boolean} [props.autoClose=false] - Флаг, указывающий, должно ли сообщение автоматически закрываться через заданное время
 * @param {number} [props.autoCloseDelay=5000] - Время в миллисекундах до автоматического закрытия сообщения (по умолчанию 5000 мс)
 * @param {React.ReactNode} [props.actions] - Дополнительные действия для отображения (например, кнопки, ссылки)
 *                                                 Отображаются в отдельном блоке под основным сообщением
 *
 * @return {JSX.Element|null} Компонент сообщения с соответствующим оформлением или null, если сообщение было скрыто
 *
 * @description
 * Компонент использует стили Bootstrap для отображения сообщений различного уровня важности:
 * - success: зеленый цвет для сообщений об успешном выполнении операций
 * - info: синий цвет для информационных сообщений
 * - warning: желтый цвет для предупреждающих сообщений
 * - error/danger: красный цвет для сообщений об ошибках
 *
 * При активации autoClose компонент автоматически скроет себя через указанное время.
 * При активации dismissible пользователь может закрыть сообщение вручную с помощью кнопки закрытия.
 */
const Alert = ({ message, level, dismissible, autoClose, autoCloseDelay, actions }) => {
  const [show, setShow] = useState(true);

  useEffect(() => {
    if (autoClose && show) {
      const timer = setTimeout(() => {
        setShow(false);
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseDelay, show]);

  if (!show) {
    return null;
  }

  const variantMap = {
    success: 'success',
    info: 'info',
    warning: 'warning',
    error: 'danger',
    danger: 'danger',
  };

  const variant = variantMap[level] || 'info';

  return (
    <BSAlert
      variant={variant}
      onClose={dismissible ? () => setShow(false) : undefined}
      dismissible={dismissible}
    >
      <div dangerouslySetInnerHTML={{ __html: message }} />
      {actions && <div className="mt-2">{actions}</div>}
    </BSAlert>
  );
};

Alert.propTypes = {
  message: PropTypes.string.isRequired,
  level: PropTypes.oneOf(['success', 'info', 'warning', 'error', 'danger']).isRequired,
  dismissible: PropTypes.bool,
  autoClose: PropTypes.bool,
  autoCloseDelay: PropTypes.number,
  actions: PropTypes.node,
};

Alert.defaultProps = {
  dismissible: true,
  autoClose: false,
  autoCloseDelay: 5000,
};

export default Alert;
