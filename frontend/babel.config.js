/**
 * @file Единая конфигурация Babel для сборки webpack и тестов Jest.
 *
 * Оба сценария подключают файл явно через configFile (см. webpack.config.js
 * и jest.config.js): настройки пресетов существуют в одном месте и не могут
 * разойтись между сборкой и тестами.
 *
 * @module babel.config
 */
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: '> 0.25%, not dead',
      },
    ],
    '@babel/preset-typescript',
  ],
  overrides: [
    {
      test: ['**/*.js', '**/*.jsx', '**/*.tsx'],
      // preset-react добавляет JSX-синтаксис во все файлы: в Babel 8 из-за
      // этого .ts перестают парситься (дженерик-стрелки вида <T>...),
      // поэтому JSX-пресет ограничен файлами, где JSX возможен.
      // development повторяет режим сборки через NODE_ENV, который явно
      // задают оба скрипта (npm run dev и npm run build): дефолт Babel 8
      // вычисляет опцию от api.env() и при отсутствии NODE_ENV включает
      // jsxDEV в production-сборке, где production-runtime React его
      // не экспортирует - бандл падает в браузере.
      presets: [['@babel/preset-react', { runtime: 'automatic', development: process.env.NODE_ENV === 'development' }]],
    },
  ],
};
