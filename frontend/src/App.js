import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppRouter } from './router/AppRouter';
import './assets/styles/global.css'; //
import CalendarDesignPage from './pages/Instagram/index';
function App() {
  return (
    <BrowserRouter>
      <div className="App min-h-screen bg-gray-50 text-gray-900">
        {/* ここに将来Headerなどを配置します */}
      <Routes>
        <Route path="/instagram" element={<InstagramGenPage/>} />
        {/* 他のルート... */}
      </Routes>
        {/* ルーティングされたページがここに表示されます */}
        <AppRouter />
      
      </div>
    </BrowserRouter>
  );Instagram
}

export default App;
