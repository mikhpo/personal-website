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
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/personal_website/frontend'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@components/(.*)$': '<rootDir>/personal_website/frontend/src/components/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/personal_website/frontend/jest.setup.js'],
  collectCoverageFrom: [
    'personal_website/frontend/src/**/*.{js,jsx}',
    '!personal_website/frontend/src/**/*.test.{js,jsx}',
    '!personal_website/frontend/src/**/__tests__/**',
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
