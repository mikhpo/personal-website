import React from 'react';
import PropTypes from 'prop-types';
import { Dropdown } from 'react-bootstrap';
import { useTheme } from '@hooks';

/**
 * Доступные варианты темы: value null означает следование системной теме
 */
const THEME_OPTIONS = [
  { value: 'light', label: 'Светлая', icon: 'bi-sun-fill' },
  { value: 'dark', label: 'Тёмная', icon: 'bi-moon-stars-fill' },
  { value: null, label: 'Системная', icon: 'bi-circle-half' },
];

/**
 * Компонент переключения темы сайта (светлая, темная, системная)
 *
 * Кнопка отражает текущее состояние иконкой, выпадающее меню позволяет выбрать тему.
 * Выбор сохраняется в localStorage, режим "Системная" следует за темой браузера.
 *
 * @param {Object} props - Свойства компонента
 * @param {string} [props.variant="outline-secondary"] - Вариант кнопки Bootstrap
 *
 * @return {JSX.Element} Элемент выпадающего меню выбора темы
 *
 * @example
 * // Размещение в навигационной панели
 * <ThemeToggle />
 */
const ThemeToggle = ({ variant }) => {
  const { theme, storedTheme, setTheme } = useTheme();

  // В режиме "Системная" иконка кнопки показывает автоматический режим,
  // иначе - действующую тему
  const toggleIcon =
    storedTheme === null ? 'bi-circle-half' : theme === 'dark' ? 'bi-moon-stars-fill' : 'bi-sun-fill';

  return (
    <Dropdown align="end" className="navbar-theme my-2 my-lg-0">
      <Dropdown.Toggle variant={variant} title="Выбор темы" aria-label="Выбор темы">
        <i className={`bi ${toggleIcon}`} aria-hidden="true" />
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {THEME_OPTIONS.map(({ value, label, icon }) => {
          const isActive = storedTheme === null ? value === null : value === storedTheme;
          return (
            <Dropdown.Item key={label} active={isActive} onClick={() => setTheme(value)}>
              <i className={`bi ${icon} me-2`} aria-hidden="true" />
              {label}
            </Dropdown.Item>
          );
        })}
      </Dropdown.Menu>
    </Dropdown>
  );
};

ThemeToggle.propTypes = {
  variant: PropTypes.string,
};

ThemeToggle.defaultProps = {
  variant: 'outline-secondary',
};

export default ThemeToggle;
