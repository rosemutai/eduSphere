// @type {import('tailwindcss').Config} 

module.exports = {
    content: [
      './templates/base.html',
      './school/templates/**/*.html',
      './school/templates/**/*.html',
      // Add any other app template paths here
    ],
    theme: {
      colors: {
        'lightblue': '#60B5FF'
      },
      extend: {},
    },
    plugins: [],
  }
  