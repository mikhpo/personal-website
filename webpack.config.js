const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
  entry: {
    main: './personal_website/frontend/src/index.js',
  },
  output: {
    path: path.resolve(__dirname, 'personal_website/frontend/dist'),
    filename: '[name]-[contenthash].js',
    publicPath: '/static/frontend/dist/',
  },
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
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@components': path.resolve(__dirname, 'personal_website/frontend/src/components'),
      '@utils': path.resolve(__dirname, 'personal_website/frontend/src/utils'),
    },
  },
  plugins: [
    new CleanWebpackPlugin(),
    new BundleTracker({
      path: __dirname,
      filename: 'webpack-stats.json',
    }),
  ],
  devtool: 'source-map',
};
