import React from 'react';
import PropTypes from 'prop-types';

/**
 * Тестовый компонент для проверки интеграции React
 * @param {Object} props - Свойства компонента
 * @param {string} props.message - Сообщение для отображения
 * @return {JSX.Element} Отрендеренный компонент
 */
const TestComponent = ({ message }) => {
  return (
    <div className="alert alert-success" role="alert">
      <h4 className="alert-heading">React работает!</h4>
      <p>{message}</p>
    </div>
  );
};

TestComponent.propTypes = {
  message: PropTypes.string,
};

TestComponent.defaultProps = {
  message: 'React успешно интегрирован в Django проект',
};

export default TestComponent;
