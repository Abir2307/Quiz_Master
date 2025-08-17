// vue.config.js
module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/admin': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/user': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/quizzes': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/subjects': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/check_session': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
};
