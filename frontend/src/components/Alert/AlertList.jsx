import React from 'react';
import PropTypes from 'prop-types';
import Alert from '@components/Alert/AlertDetail';

/**
 * Компонент для отображения списка сообщений.
 *
 * Отображает коллекцию сообщений различного уровня важности. Представляет собой
 * компонент типа Collection, который управляет массивом отдельных компонентов Alert.
 *
 * @component
 * @example
 * // Пример использования компонента с массивом сообщений
 * const messages = [
 *   { message: "Операция выполнена успешно!", level: "success", dismissible: true },
 *   { message: "Внимание! Требуется подтверждение действия.", level: "warning", autoClose: true }
 * ];
 *
 * <AlertList messages={messages} />
 *
 * @param {Object} props - Свойства компонента
 * @param {Array<Object>} props.messages - Массив сообщений для отображения
 * @param {string} props.messages[].message - Текст сообщения для отображения
 * @param {('success'|'info'|'warning'|'error'|'danger')} props.messages[].level - Уровень важности
 * @param {oolean} [props.messages[].dismissible] - Возможность ручного закрытия
 * @param {Boolean} [props.messages[].autoClose] - Автоматическое закрытие
 * @param {number} [props.messages[].autoCloseDelay] - Время до авто-закрытия в мс
 * @param {React.ReactNode} [props.messages[].actions] - Дополнительные действия для отображения
 *
 * @return {JSX.Element|null} Компонент списка сообщений или null при их отсутствии
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
 *
 * @note
 * Используется для общих системных уведомлений (например,
 * результаты формы, статусные сообщения, уведомления о действиях пользователя).
 */
const AlertList = ({ messages }) => {
  if (!messages || messages.length === 0) {
    return null;
  }

  return (
    <div className="container mt-3">
      {messages.map((msg) => (
        <Alert
          key={`${msg.level}-${msg.message}`}
          message={msg.message}
          level={msg.level}
          dismissible={msg.dismissible !== false}
          autoClose={msg.autoClose || false}
          autoCloseDelay={msg.autoCloseDelay || 5000}
          actions={msg.actions}
        />
      ))}
    </div>
  );
};

AlertList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      message: PropTypes.string.isRequired,
      level: PropTypes.string.isRequired,
      dismissible: PropTypes.bool,
      autoClose: PropTypes.bool,
      autoCloseDelay: PropTypes.number,
      actions: PropTypes.node,
    })
  ),
};

AlertList.defaultProps = {
  messages: [],
};

export default AlertList;
