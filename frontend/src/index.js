import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
// ▼▼▼ ここが重要！作成したCSSファイルを読み込みます ▼▼▼
import './assets/styles/global.css';
import { AppRouter } from './router/AppRouter';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      {/* App.jsではなくRouterを直接呼ぶ、またはApp.js経由にする */}
      {/* 今回の構成に合わせてAppRouterを直接描画します */}
      <AppRouter />
    </BrowserRouter>
  </React.StrictMode>
);
