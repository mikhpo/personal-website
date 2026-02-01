import React from 'react';
import { render, screen } from '@testing-library/react';
import Navbar from './Navbar';

describe('Navbar', () => {
  const defaultProps = {
    brandName: 'Мой сайт',
    brandUrl: '/',
    links: [
      { url: '/', text: 'Главная', active: false },
      { url: '/blog/', text: 'Блог', active: false },
      {
        url: '/gallery/',
        text: 'Галерея',
        active: false,
        dropdown: [
          { url: '/gallery/albums/', text: 'Альбомы' },
          { url: '/gallery/photos/', text: 'Фотографии' },
          { url: '/gallery/tags/', text: 'Тэги' },
        ]
      },
    ],
    userAuthenticated: false,
    userIsStaff: false,
  };

  test('рендерит навигацию для неавторизованного пользователя', () => {
    render(<Navbar {...defaultProps} />);

    expect(screen.getByText('Мой сайт')).toBeInTheDocument();
    expect(screen.getByText('Главная')).toBeInTheDocument();
    expect(screen.getByText('Блог')).toBeInTheDocument();
    expect(screen.getByText('Галерея')).toBeInTheDocument();
    expect(screen.getByText('Войти')).toBeInTheDocument();
    expect(screen.getByText('Регистрация')).toBeInTheDocument();

    // Проверяем, что dropdown элементы не отображаются по умолчанию
    expect(screen.queryByText('Альбомы')).not.toBeInTheDocument();
  });

  test('рендерит навигацию для авторизованного пользователя', () => {
    const props = {
      ...defaultProps,
      userAuthenticated: true,
      userName: 'testuser',
    };

    render(<Navbar {...props} />);

    expect(screen.getByText(/Вы вошли как testuser/)).toBeInTheDocument();
    expect(screen.getByText('Выйти')).toBeInTheDocument();
    expect(screen.queryByText('Войти')).not.toBeInTheDocument();
  });

  test('рендерит дополнительные элементы для staff пользователя', () => {
    const props = {
      ...defaultProps,
      userAuthenticated: true,
      userIsStaff: true,
      userName: 'staffuser',
    };

    render(<Navbar {...props} />);

    expect(screen.getByText('Администрирование')).toBeInTheDocument();
  });
});
