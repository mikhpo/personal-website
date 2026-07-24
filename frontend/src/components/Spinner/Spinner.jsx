import React from 'react';
import { Spinner } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Компонент индикатора загрузки.
 *
 * Отображает спиннер Bootstrap с настраиваемым сообщением.
 *
 * @param {Object} props - Пропсы компонента
 * @param {string} [props.message="Загрузка..."] - Текст сообщения под спиннером
 * @return {JSX.Element} Компонент индикатора загрузки
 */
const SpinnerComponent = ({ message = 'Загрузка...' }) => {
  return (
    <div className="text-center my-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">{message}</span>
      </Spinner>
      <p className="mt-3">{message}</p>
    </div>
  );
};

SpinnerComponent.propTypes = {
  message: PropTypes.string,
};

export default SpinnerComponent;
