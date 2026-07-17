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
const CopyWebpackPlugin = require('copy-webpack-plugin');

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
      '@ui': path.resolve(__dirname, 'src/ui'),
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
    // TinyMCE в отличие от обычных npm-пакетов не может быть полностью включён в бандл:
    // во время работы редактор динамически загружает плагины, темы и скины через отдельные
    // HTTP-запросы по статическим URL (например, /static/tinymce/themes/silver/theme.min.js).
    // Webpack не знает об этих файлах, поэтому копируем всю папку node_modules/tinymce
    // в dist/tinymce/ — откуда Django раздаёт их по URL /static/tinymce/.
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, '../node_modules/tinymce'),
          to: path.resolve(__dirname, 'dist/tinymce'),
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
