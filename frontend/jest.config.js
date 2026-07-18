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
 * - collectCoverageFrom: Паттерны файлов для сбора информации о покрытии кода тестами
 * - coverageThreshold: Минимальные требования к покрытию кода тестами (в процентах)
 */
const frontendDir = __dirname;

module.exports = {
  testEnvironment: 'jsdom',
  rootDir: frontendDir,
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@components$': '<rootDir>/src/components/index.js',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@services$': '<rootDir>/src/services/index.js',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@utils$': '<rootDir>/src/utils/index.js',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@hooks$': '<rootDir>/src/hooks/index.js',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.test.{js,jsx}',
    '!src/**/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      statements: 70,
      branches: 70,
      functions: 70,
      lines: 70,
    },
  },
};
