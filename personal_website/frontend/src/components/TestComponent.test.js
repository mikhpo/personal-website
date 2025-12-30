import React from 'react';
import { render, screen } from '@testing-library/react';
import TestComponent from './TestComponent';

/**
 * Набор тестов для компонента TestComponent
 * Проверяет корректность отображения компонента с сообщением по умолчанию и с кастомным сообщением
 * @module TestComponent.test
 */
describe('TestComponent', () => {
  test('рендерит компонент с сообщением по умолчанию', () => {
    render(<TestComponent />);
    expect(screen.getByText('React работает!')).toBeInTheDocument();
    expect(screen.getByText(/React успешно интегрирован/)).toBeInTheDocument();
  });

  test('рендерит компонент с кастомным сообщением', () => {
    const customMessage = 'Тестовое сообщение';
    render(<TestComponent message={customMessage} />);
    expect(screen.getByText(customMessage)).toBeInTheDocument();
  });
});
