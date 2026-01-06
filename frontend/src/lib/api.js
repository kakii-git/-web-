import axios from 'axios';

// バックエンドのURL (環境変数から読み込むか、なければlocalhost:8000)
// Reactでは環境変数は REACT_APP_ から始める必要があります
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axiosのインスタンスを作成
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエスト送信前の処理 (インターセプター)
// 毎回リクエストを送る前に、自動で「通行手形（トークン）」をヘッダーにくっつけます
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// レスポンス受信後の処理
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 認証エラー(401)が出たら、コンソールに表示したりログアウトさせたりする処理をここに書けます
    return Promise.reject(error);
  }
);

export default api;