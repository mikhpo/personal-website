/**
 * @file Конфигурационный файл для тестового фреймворка Jest
 *
 * Этот файл содержит настройки для запуска тестов в проекте с использованием Jest.
 * Основные настройки включают:
 * - testEnvironment: Окружение для выполнения тестов (jsdom для браузероподобного окружения)
 * - roots: Корневые директории для поиска тестов
 * - testMatch: Паттерны для поиска файлов с тестами
 * - moduleNameMapper: Сопоставление импортов модулей (для CSS файлов и алиасов)
 * - setupFilesAfterEnv: Файлы настройки, выполняемые перед запуском тестов
 * - modulePathIgnorePatterns: Пути, исключаемые из поиска модулей (например,
 *   результат collectstatic в backend/static, дублирующий пакеты node_modules)
 * - collectCoverageFrom: Паттерны файлов для сбора информации о покрытии кода тестами
 * - coverageThreshold: Минимальные требования к покрытию кода тестами (в процентах)
 */
const frontendDir = __dirname;

module.exports = {
  testEnvironment: 'jsdom',
  rootDir: frontendDir,
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/__tests__/**/*.tsx', '**/?(*.)+(spec|test).ts', '**/?(*.)+(spec|test).tsx'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@services$': '<rootDir>/src/services/index.ts',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@hooks$': '<rootDir>/src/hooks/index.ts',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  // Исключаем результат collectstatic: backend/static
  // содержит дубликаты пакетов из node_modules.
  modulePathIgnorePatterns: ['<rootDir>/../backend/static'],
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}', '!src/**/*.test.{js,jsx,ts,tsx}', '!src/**/__tests__/**'],
  coverageThreshold: {
    global: {
      statements: 70,
      branches: 70,
      functions: 70,
      lines: 70,
    },
  },
};
