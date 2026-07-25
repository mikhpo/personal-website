import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoadingError from '@components/Alert/LoadingError';

describe('LoadingError', () => {
  it('отображает сообщение об ошибке и кнопку повтора', () => {
    const mockRetry = jest.fn();
    render(<LoadingError message="Тестовая ошибка" onRetry={mockRetry} />);

    expect(screen.getByText('Тестовая ошибка')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Повторить' })).toBeInTheDocument();
  });

  it('вызывает onRetry при нажатии на кнопку', () => {
    const mockRetry = jest.fn();
    render(<LoadingError message="Тестовая ошибка" onRetry={mockRetry} />);

    const button = screen.getByRole('button', { name: 'Повторить' });
    fireEvent.click(button);

    expect(mockRetry).toHaveBeenCalledTimes(1);
  });

  it('отображает пользовательский текст кнопки повтора', () => {
    render(<LoadingError message="Тестовая ошибка" onRetry={jest.fn()} retryButtonText="Попробовать снова" />);

    expect(screen.getByRole('button', { name: 'Попробовать снова' })).toBeInTheDocument();
  });
});
