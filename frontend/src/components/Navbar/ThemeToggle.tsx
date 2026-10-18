import React from 'react';
import { Dropdown } from 'react-bootstrap';
import { useTheme, type ThemeName } from '@hooks';

/** Пункт меню выбора темы. */
interface ThemeOption {
  /** value null означает следование системной теме. */
  value: ThemeName | null;
  label: string;
  icon: string;
}

/**
 * Доступные варианты темы.
 */
const THEME_OPTIONS: ThemeOption[] = [
  { value: 'light', label: 'Светлая', icon: 'bi-sun-fill' },
  { value: 'dark', label: 'Тёмная', icon: 'bi-moon-stars-fill' },
  { value: null, label: 'Системная', icon: 'bi-circle-half' },
];

/** Свойства компонента переключения темы. */
export interface ThemeToggleProps {
  /** Вариант кнопки Bootstrap. */
  variant?: string;
}

/**
 * Компонент переключения темы сайта (светлая, темная, системная).
 *
 * Кнопка отражает текущее состояние иконкой, выпадающее меню позволяет выбрать
 * тему. Выбор сохраняется в localStorage, режим "Системная" следует за темой
 * браузера.
 *
 * @example
 * <ThemeToggle />
 */
const ThemeToggle = ({ variant = 'outline-secondary' }: ThemeToggleProps) => {
  const { theme, storedTheme, setTheme } = useTheme();

  // В режиме "Системная" иконка кнопки показывает автоматический режим,
  // иначе - действующую тему
  const toggleIcon = storedTheme === null ? 'bi-circle-half' : theme === 'dark' ? 'bi-moon-stars-fill' : 'bi-sun-fill';

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

export default ThemeToggle;
