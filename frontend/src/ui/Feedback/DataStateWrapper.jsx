import React from 'react';
import PropTypes from 'prop-types';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';

/**
 * Компонент-обёртка для отображения различных состояний данных.
 *
 * Унифицирует обработку состояний загрузки, ошибки, пустых данных и успешного отображения.
 * Заменяет дублирующийся код обработки этих состояний в компонентах списков.
 *
 * @param {Object} props - Пропсы компонента
 * @param {boolean} props.loading - Состояние загрузки
 * @param {string|null} props.error - Сообщение об ошибке или null
 * @param {boolean} props.empty - Отображать ли состояние пустых данных
 * @param {React.ReactNode} props.children - Дочерние элементы для отображения при успехе
 * @param {string} [props.loadingMessage="Загрузка..."] - Сообщение при загрузке
 * @param {string} [props.emptyMessage="Нет данных"] - Сообщение при отсутствии данных
 * @param {Function} [props.onRetry] - Callback для повторной попытки
 * @param {string} [props.errorLevel="error"] - Уровень отображения ошибки
 * @return {JSX.Element} Компонент с соответствующим состоянием
 *
 * @example
 * // Базовое использование
 * <DataStateWrapper
 *   loading={loading}
 *   error={error}
 *   empty={items.length === 0}
 *   loadingMessage="Загрузка статей..."
 *   emptyMessage="Статьи не найдены"
 *   onRetry={() => refetch()}
 * >
 *   {items.map(item => <ItemCard key={item.id} item={item} />)}
 * </DataStateWrapper>
 *
 * @example
 * // С пустым состоянием ошибки
 * <DataStateWrapper loading={loading} error={null} empty={false}>
 *   <div>Контент для отображения</div>
 * </DataStateWrapper>
 */
const DataStateWrapper = ({
  loading,
  error,
  empty,
  children,
  loadingMessage = 'Загрузка...',
  emptyMessage = 'Нет данных',
  onRetry,
  errorLevel = 'error',
}) => {
  // Отображение индикатора загрузки
  if (loading) {
    return <SpinnerComponent message={loadingMessage} />;
  }

  // Отображение сообщения об ошибке
  if (error) {
    const messages = [{ message: error, level: errorLevel }];

    if (onRetry) {
      messages[0].actions = (
        <button
          type="button"
          className="btn btn-outline-primary btn-sm"
          onClick={onRetry}
        >
          Повторить
        </button>
      );
    }

    return <AlertList messages={messages} />;
  }

  // Отображение сообщения о пустом списке
  if (empty) {
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  // Отображение дочерних элементов
  return <>{children}</>;
};

DataStateWrapper.propTypes = {
  loading: PropTypes.bool.isRequired,
  error: PropTypes.string,
  empty: PropTypes.bool.isRequired,
  children: PropTypes.node,
  loadingMessage: PropTypes.string,
  emptyMessage: PropTypes.string,
  onRetry: PropTypes.func,
  errorLevel: PropTypes.oneOf(['error', 'warning', 'info']),
};

export default DataStateWrapper;
