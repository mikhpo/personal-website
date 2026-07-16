import {
  isButtonDisabled,
  getButtonHref,
  getButtonText,
  getButtonClassName
} from './buttonStates';

/**
 * Тесты для утилит состояний кнопок
 */
describe('buttonStates', () => {
  /**
   * Тесты для функции isButtonDisabled
   */
  describe('isButtonDisabled', () => {
    test('кнопка "первая" отключена на первой странице', () => {
      expect(isButtonDisabled('first', 1, 5)).toBe(true);
    });

    test('кнопка "первая" включена не на первой странице', () => {
      expect(isButtonDisabled('first', 2, 5)).toBe(false);
    });

    test('кнопка "предыдущая" отключена на первой странице', () => {
      expect(isButtonDisabled('prev', 1, 5)).toBe(true);
    });

    test('кнопка "предыдущая" включена не на первой странице', () => {
      expect(isButtonDisabled('prev', 2, 5)).toBe(false);
    });

    test('кнопка "следующая" отключена на последней странице', () => {
      expect(isButtonDisabled('next', 5, 5)).toBe(true);
    });

    test('кнопка "следующая" включена не на последней странице', () => {
      expect(isButtonDisabled('next', 4, 5)).toBe(false);
    });

    test('кнопка "последняя" отключена на последней странице', () => {
      expect(isButtonDisabled('last', 5, 5)).toBe(true);
    });

    test('кнопка "последняя" включена не на последней странице', () => {
      expect(isButtonDisabled('last', 4, 5)).toBe(false);
    });
  });

  /**
   * Тесты для функции getButtonHref
   */
  describe('getButtonHref', () => {
    test('возвращает undefined для отключенной кнопки', () => {
      expect(getButtonHref('first', 1, 5, '/blog/')).toBeUndefined();
    });

    test('возвращает правильный URL для кнопки "первая"', () => {
      expect(getButtonHref('first', 2, 5, '/blog/')).toBe('/blog/?page=1');
    });

    test('возвращает правильный URL для кнопки "предыдущая"', () => {
      expect(getButtonHref('prev', 3, 5, '/blog/')).toBe('/blog/?page=2');
    });

    test('возвращает правильный URL для кнопки "следующая"', () => {
      expect(getButtonHref('next', 3, 5, '/blog/')).toBe('/blog/?page=4');
    });

    test('возвращает правильный URL для кнопки "последняя"', () => {
      expect(getButtonHref('last', 3, 5, '/blog/')).toBe('/blog/?page=5');
    });
  });

  /**
   * Тесты для функции getButtonText
   */
  describe('getButtonText', () => {
    test('возвращает правильный текст для кнопки "первая"', () => {
      expect(getButtonText('first')).toBe('первая');
    });

    test('возвращает правильный текст для кнопки "предыдущая"', () => {
      expect(getButtonText('prev')).toBe('предыдущая');
    });

    test('возвращает правильный текст для кнопки "следующая"', () => {
      expect(getButtonText('next')).toBe('следующая');
    });

    test('возвращает правильный текст для кнопки "последняя"', () => {
      expect(getButtonText('last')).toBe('последняя');
    });
  });

  /**
   * Тесты для функции getButtonClassName
   */
  describe('getButtonClassName', () => {
    test('возвращает правильные классы для кнопки "первая"', () => {
      expect(getButtonClassName('first')).toBe('btn btn-outline-dark me-1');
    });

    test('возвращает правильные классы для кнопки "предыдущая"', () => {
      expect(getButtonClassName('prev')).toBe('btn btn-outline-dark me-1');
    });

    test('возвращает правильные классы для кнопки "следующая"', () => {
      expect(getButtonClassName('next')).toBe('btn btn-outline-dark ms-1');
    });

    test('возвращает правильные классы для кнопки "последняя"', () => {
      expect(getButtonClassName('last')).toBe('btn btn-outline-dark ms-1');
    });
  });
});
