/**
 * Тесты для компонента DataStateWrapper.
 *
 * Проверяют корректность отображения различных состояний данных:
 * загрузки, ошибки, пустых данных и успешного отображения контента.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DataStateWrapper from './DataStateWrapper';

describe('DataStateWrapper', () => {
  const mockChildren = <div data-testid="content">Контент для отображения</div>;

  /**
   * Проверяет состояние загрузки.
   */
  describe('loading состояние', () => {
    test('отображает спиннер когда loading=true', () => {
      render(<DataStateWrapper loading={true} error={null} empty={false} />);
      expect(screen.getAllByText('Загрузка...').length).toBeGreaterThan(0);
    });

    test('отображает кастомное сообщение при загрузке', () => {
      render(
        <DataStateWrapper
          loading={true}
          error={null}
          empty={false}
          loadingMessage="Загрузка статей..."
        />
      );
      expect(screen.getAllByText('Загрузка статей...').length).toBeGreaterThan(0);
    });

    test('не отображает children когда loading=true', () => {
      render(
        <DataStateWrapper loading={true} error={null} empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет состояние ошибки.
   */
  describe('error состояние', () => {
    test('отображает ошибку когда error задан', () => {
      render(
        <DataStateWrapper loading={false} error="Ошибка загрузки данных" empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Ошибка загрузки данных')).toBeInTheDocument();
    });

    test('не отображает children когда есть ошибка', () => {
      render(
        <DataStateWrapper loading={false} error="Ошибка" empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    });

    test('отображает кнопку Повторить когда передан onRetry', () => {
      const mockRetry = jest.fn();
      render(
        <DataStateWrapper
          loading={false}
          error="Ошибка"
          empty={false}
          onRetry={mockRetry}
        >
          {mockChildren}
        </DataStateWrapper>
      );

      const button = screen.getByText('Повторить');
      expect(button).toBeInTheDocument();
      expect(button.tagName).toBe('BUTTON');
    });

    test('вызывает onRetry при клике на кнопку Повторить', () => {
      const mockRetry = jest.fn();
      render(
        <DataStateWrapper
          loading={false}
          error="Ошибка"
          empty={false}
          onRetry={mockRetry}
        >
          {mockChildren}
        </DataStateWrapper>
      );

      const button = screen.getByText('Повторить');
      fireEvent.click(button);
      expect(mockRetry).toHaveBeenCalledTimes(1);
    });

    test('не отображает кнопку Повторить когда onRetry не передан', () => {
      render(
        <DataStateWrapper loading={false} error="Ошибка" empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.queryByText('Повторить')).not.toBeInTheDocument();
    });

    test('поддерживает различные errorLevel', () => {
      const { rerender } = render(
        <DataStateWrapper loading={false} error="Warning" empty={false} errorLevel="warning">
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Warning')).toBeInTheDocument();

      rerender(
        <DataStateWrapper loading={false} error="Info" empty={false} errorLevel="info">
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Info')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет состояние пустых данных.
   */
  describe('empty состояние', () => {
    test('отображает сообщение когда empty=true', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={true}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Нет данных')).toBeInTheDocument();
    });

    test('отображает кастомное сообщение для empty', () => {
      render(
        <DataStateWrapper
          loading={false}
          error={null}
          empty={true}
          emptyMessage="Статьи не найдены"
        >
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Статьи не найдены')).toBeInTheDocument();
    });

    test('не отображает children когда empty=true', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={true}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    });

    test('показывает empty сообщение даже при наличии children', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={true}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Нет данных')).toBeInTheDocument();
      expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет успешное состояние.
   */
  describe('успешное состояние', () => {
    test('отображает children когда нет loading, error и empty', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByTestId('content')).toBeInTheDocument();
      expect(screen.getByText('Контент для отображения')).toBeInTheDocument();
    });

    test('не отображает спиннер или сообщение об ошибке', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument();
      expect(screen.queryByText('Нет данных')).not.toBeInTheDocument();
    });

    test('отображает несколько children компонентов', () => {
      const multipleChildren = (
        <>
          <div data-testid="item1">Элемент 1</div>
          <div data-testid="item2">Элемент 2</div>
        </>
      );

      render(
        <DataStateWrapper loading={false} error={null} empty={false}>
          {multipleChildren}
        </DataStateWrapper>
      );

      expect(screen.getByTestId('item1')).toBeInTheDocument();
      expect(screen.getByTestId('item2')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет приоритет состояний.
   */
  describe('приоритет состояний', () => {
    test('loading имеет приоритет над empty', () => {
      render(
        <DataStateWrapper loading={true} error={null} empty={true}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getAllByText('Загрузка...').length).toBeGreaterThan(0);
      expect(screen.queryByText('Нет данных')).not.toBeInTheDocument();
    });

    test('loading имеет приоритет над error', () => {
      render(
        <DataStateWrapper loading={true} error="Ошибка" empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getAllByText('Загрузка...').length).toBeGreaterThan(0);
      expect(screen.queryByText('Ошибка')).not.toBeInTheDocument();
    });

    test('error имеет приоритет над empty', () => {
      render(
        <DataStateWrapper loading={false} error="Ошибка" empty={true}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByText('Ошибка')).toBeInTheDocument();
      expect(screen.queryByText('Нет данных')).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет крайние случаи.
   */
  describe('крайние случаи', () => {
    test('обрабатывает null как отсутствие ошибки', () => {
      render(
        <DataStateWrapper loading={false} error={null} empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    test('обрабатывает undefined как отсутствие ошибки', () => {
      render(
        <DataStateWrapper loading={false} error={undefined} empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    test('обрабатывает пустую строку как отсутствие ошибки', () => {
      render(
        <DataStateWrapper loading={false} error="" empty={false}>
          {mockChildren}
        </DataStateWrapper>
      );
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });
  });
});
