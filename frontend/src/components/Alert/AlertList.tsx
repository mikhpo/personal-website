import React from 'react';
import Alert, { type AlertProps } from '@components/Alert/AlertDetail';

/** Одно сообщение списка: свойства Alert без неизменяемой части. */
export type AlertMessage = Pick<
  AlertProps,
  'message' | 'level' | 'dismissible' | 'autoClose' | 'autoCloseDelay' | 'actions'
>;

/** Свойства компонента списка сообщений. */
export interface AlertListProps {
  /** Массив сообщений для отображения. */
  messages?: AlertMessage[];
}

/**
 * Компонент для отображения списка сообщений.
 *
 * Отображает коллекцию сообщений различного уровня важности. Представляет собой
 * компонент типа Collection, который управляет массивом отдельных компонентов
 * Alert. При отсутствии сообщений возвращает null.
 *
 * Используется для общих системных уведомлений (например, результаты формы,
 * статусные сообщения, уведомления о действиях пользователя).
 *
 * @example
 * <AlertList
 *   messages={[
 *     { message: 'Операция выполнена успешно!', level: 'success', dismissible: true },
 *     { message: 'Внимание! Требуется подтверждение действия.', level: 'warning', autoClose: true },
 *   ]}
 * />
 */
const AlertList = ({ messages = [] }: AlertListProps) => {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="container mt-3">
      {messages.map((msg, index) => (
        <Alert
          // eslint-disable-next-line react-x/no-array-index-key -- сообщения могут дублироваться, и content-ключ дал бы дубли; идентичность алертов между рендерами не требуется
          key={index}
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

export default AlertList;
