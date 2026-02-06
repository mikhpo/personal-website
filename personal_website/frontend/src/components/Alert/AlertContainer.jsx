/* eslint-disable valid-jsdoc */
import React from 'react';
import PropTypes from 'prop-types';
import Alert from './Alert';

/**
 * Контейнер для отображения множественных сообщений.
 *
 * Отображает список сообщений различного уровня важности. Используется для
 * централизованного управления отображением системных уведомлений.
 *
 * @component
 * @example
 * // Пример использования контейнера с массивом сообщений
 * const messages = [
 *   { message: "Операция выполнена успешно!", level: "success", dismissible: true },
 *   { message: "Внимание! Требуется подтверждение действия.", level: "warning", autoClose: true }
 * ];
 *
 * <AlertContainer messages={messages} />
 *
 * @param {Object} props - Свойства компонента
 * @param {Array<Object>} props.messages - Массив сообщений для отображения
 * @param {string} props.messages[].message - Текст сообщения для отображения
 * @param {('success'|'info'|'warning'|'error'|'danger')} props.messages[].level - Уровень важности
 * @param {boolean} [props.messages[].dismissible] - Возможность ручного закрытия
 * @param {boolean} [props.messages[].autoClose=false] - Автоматическое закрытие
 * @param {number} [props.messages[].autoCloseDelay=5000] - Время до авто-закрытия в мс
 *
 * @return {JSX.Element|null} Контейнер с сообщениями или null при их отсутствии
 *
 * @description
 * Компонент принимает массив сообщений и отображает каждый элемент как
 * отдельный компонент Alert. При отсутствии сообщений возвращает null.
 *
 * Поддерживаемые уровни важности:
 * - success: зеленый цвет для успешных операций
 * - info: синий цвет для информационных сообщений
 * - warning: желтый цвет для предупреждений
 * - error/danger: красный цвет для ошибок
 */
const AlertContainer = ({ messages }) => {
  if (!messages || messages.length === 0) {
    return null;
  }

  return (
    <div className="container mt-3">
      {messages.map((msg, index) => (
        <Alert
          key={`${msg.level}-${index}`}
          message={msg.message}
          level={msg.level}
          dismissible={msg.dismissible !== false}
          autoClose={msg.autoClose || false}
          autoCloseDelay={msg.autoCloseDelay || 5000}
        />
      ))}
    </div>
  );
};

AlertContainer.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      message: PropTypes.string.isRequired,
      level: PropTypes.string.isRequired,
      dismissible: PropTypes.bool,
      autoClose: PropTypes.bool,
      autoCloseDelay: PropTypes.number,
    })
  ),
};

AlertContainer.defaultProps = {
  messages: [],
};

export default AlertContainer;
