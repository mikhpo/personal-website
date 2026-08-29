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
const fs = require('fs');
const BundleTracker = require('webpack-bundle-tracker');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

// backend/staticfiles стоит раньше frontend/dist в STATICFILES_DIRS:
// случайно оставшиеся там tinymce и bootstrap затеняют свежие файлы.
fs.rmSync(path.resolve(__dirname, '../backend/staticfiles/bootstrap'), { recursive: true, force: true });
fs.rmSync(path.resolve(__dirname, '../backend/staticfiles/tinymce'), { recursive: true, force: true });

module.exports = {
  /**
   * Точка входа в приложение.
   * Определяет начальные файлы для сборки.
   */
  entry: {
    main: path.resolve(__dirname, 'src/index.js'),
  },

  /**
   * Настройки выходного каталога и именования файлов.
   * Определяет, где и как будут сохранены собранные файлы.
   */
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name]-[contenthash].js',
    // publicPath определяет URL-префикс бандлов (включая lazy-chunks) в webpack-stats.json.
    // Значение берется из переменной окружения WEBPACK_PUBLIC_PATH и должно совпадать
    // со STATIC_URL той среды, для которой выполняется сборка (локально '/static/',
    // в S3-режиме - адрес бакета или CDN с префиксом static/).
    publicPath: process.env.WEBPACK_PUBLIC_PATH || '/static/',
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
      {
        test: /\.(woff|woff2|ttf|eot|svg)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name][ext]',
        },
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
      '@components': path.resolve(__dirname, 'src/components'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
    },
  },

  /**
   * Плагины Webpack.
   */
  plugins: [
    // Очищает папку dist/ перед каждой пересборкой, чтобы устаревшие файлы с прошлыми
    // хешами в именах (например, main-abc123.js) не накапливались между сборками.
    new CleanWebpackPlugin(),
    // Генерирует webpack-stats.json с информацией о собранных бандлах (имена, хеши, пути).
    // django-webpack-loader читает этот файл, чтобы подключать правильные файлы в шаблонах.
    new BundleTracker({
      path: __dirname,
      filename: 'webpack-stats.json',
    }),
    // TinyMCE и Bootstrap в отличие от обычных npm-пакетов не могут быть полностью включены
    // в бандл: редактор динамически загружает плагины, темы и скины через отдельные
    // HTTP-запросы по статическим URL (например, /static/tinymce/themes/silver/theme.min.js),
    // а стили и скрипты Bootstrap подключаются в шаблонах как отдельные файлы.
    // Webpack не знает об этих файлах, поэтому копируем их в выходной каталог сборки -
    // Django раздаёт их по тем же URL /static/tinymce/ и /static/bootstrap/dist/.
    // Такой копией вместо каталога node_modules в STATICFILES_DIRS объём статики
    // сокращается с десятков тысяч файлов до нескольких сотен. Все артефакты сборки
    // попадают в frontend/dist - единственный каталог, который переносится в Docker-образ.
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, '../node_modules/tinymce'),
          to: path.resolve(__dirname, 'dist/tinymce'),
        },
        {
          from: path.resolve(__dirname, '../node_modules/bootstrap/dist'),
          to: path.resolve(__dirname, 'dist/bootstrap/dist'),
        },
      ],
    }),
  ],

  /**
   * Настройки карты кода.
   * Позволяет отлаживать исходный код в браузере.
   */
  devtool: 'source-map',
};
