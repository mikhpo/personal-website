/**
 * Конфигурационный файл Webpack для сборки фронтенд-ресурсов.
 *
 * Этот файл настраивает сборку JavaScript и CSS файлов для проекта,
 * включая транспиляцию кода, обработку модулей, создание карты кода
 * и генерацию статистики сборки.
 *
 * @module webpack.config
 * @author Mikhail Polyakov
 * @version 1.0.0
 */
const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
  /**
   * Точка входа в приложение.
   * Определяет начальные файлы для сборки.
   */
  entry: {
    main: './personal_website/frontend/src/index.js',
  },

  /**
   * Настройки выходного каталога и именования файлов.
   * Определяет, где и как будут сохранены собранные файлы.
   */
  output: {
    path: path.resolve(__dirname, 'personal_website/frontend/dist'),
    filename: '[name]-[contenthash].js',
    publicPath: '/static/',
  },

  /**
   * Правила обработки различных типов файлов.
   * Определяет, как Webpack должен обрабатывать JavaScript, JSX и CSS файлы.
   */
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },

  /**
   * Настройки разрешения модулей.
   * Определяет расширения файлов и алиасы для импортов.
   */
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@components': path.resolve(__dirname, 'personal_website/frontend/src/components'),
    },
  },

  /**
   * Плагины Webpack.
   * Определяет дополнительные инструменты для сборки.
   * Файл `webpack-stats.json` генерируется плагином `webpack-bundle-tracker` во время сборки проекта.
   * Он содержит информацию о созданных бандлах (их имена, хеши, пути), которую использует `django-webpack-loader`
   * для подключения правильных файлов в Django шаблонах. Это особенно важно в production окружении,
   * где имена файлов могут содержать хеши для обхода кеширования браузером.
   */
  plugins: [
    new CleanWebpackPlugin(),
    new BundleTracker({
      path: __dirname,
      filename: 'webpack-stats.json',
    }),
  ],

  /**
   * Настройки карты кода.
   * Позволяет отлаживать исходный код в браузере.
   */
  devtool: 'source-map',
};
