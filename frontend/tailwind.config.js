/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      // フォント設定: "Inter" を優先的に使うように設定
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      // カラー設定: "primary" という名前で Indigo色 を登録
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1', // メインカラー
          600: '#4f46e5', // ボタンのホバー時などに使用
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        // 必要であればここに secondary カラーなども追加可能
      },
    },
  },
  plugins: [],
}
