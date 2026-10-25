import React from 'react';
import { Spinner as BootstrapSpinner } from 'react-bootstrap';

/** Свойства компонента индикатора загрузки. */
export interface SpinnerProps {
  /** Текст сообщения под спиннером. */
  message?: string;
}

/**
 * Компонент индикатора загрузки.
 *
 * Отображает спиннер Bootstrap с настраиваемым сообщением.
 */
const Spinner = ({ message = 'Загрузка...' }: SpinnerProps) => {
  return (
    <div className="text-center my-5">
      <BootstrapSpinner animation="border" role="status">
        <span className="visually-hidden">{message}</span>
      </BootstrapSpinner>
      <p className="mt-3">{message}</p>
    </div>
  );
};

export default Spinner;
