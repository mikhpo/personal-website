import reactX from 'eslint-plugin-react-x';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  {
    files: ['**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx'],
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
    },
    rules: {
      ...reactX.configs['recommended-typescript'].rules,
      'react-refresh/only-export-components': 'warn',
      'no-unused-vars': ['error', { varsIgnorePattern: '^React$' }],
    },
  },
  {
    ignores: [
      'node_modules/**',
      'static/**',
      'htmlcov/**',
      'personal_website/staticfiles/**',
      'personal_website/frontend/dist/**',
      '.venv/**',
      '**/*.min.js',
      '**/*.d.ts',
    ],
  },
];
