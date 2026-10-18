import reactX from 'eslint-plugin-react-x';
import reactRefresh from 'eslint-plugin-react-refresh';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettierConfig from 'eslint-config-prettier';
import tseslint from 'typescript-eslint';

const tsFiles = ['frontend/**/*.ts', 'frontend/**/*.tsx'];

export default [
  {
    files: ['frontend/**/*.js', 'frontend/**/*.jsx', 'frontend/**/*.ts', 'frontend/**/*.tsx'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        exports: 'readonly',
        describe: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        it: 'readonly',
        jest: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        global: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        URL: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
        Blob: 'readonly',
      },
    },
    settings: {
      react: {
        version: '19.2.7',
      },
    },
    plugins: {
      'react-x': reactX,
      'react-refresh': reactRefresh,
      'jsx-a11y': jsxA11y,
    },
    rules: {
      ...reactX.configs['recommended-typescript'].rules,
      ...jsxA11y.flatConfigs.recommended.rules,
      'react-refresh/only-export-components': 'warn',
      'no-unused-vars': ['error', { varsIgnorePattern: '^React$' }],
    },
  },
  // Парсер и правила typescript-eslint применяются только к TS-файлам;
  // каждый элемент recommended-набора ограничивается тем же глобом файлов
  ...tseslint.configs.recommended.map((config) => ({ ...config, files: tsFiles })),
  {
    files: tsFiles,
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { varsIgnorePattern: '^React$|^_', argsIgnorePattern: '^_' }],
    },
  },
  {
    // Отключает стилевые правила ESLint, конфликтующие с Prettier: форматирование делает только Prettier
    ...prettierConfig,
  },
  {
    ignores: [
      'node_modules/**',
      'static/**',
      'htmlcov/**',
      'backend/static/**',
      'static/**',
      'dist/**',
      'frontend/dist/**',
      'frontend/coverage/**',
      '.venv/**',
      '**/*.min.js',
      '**/*.d.ts',
    ],
  },
];
