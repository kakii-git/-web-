import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../lib/api'; // api設定を読み込み

const SigninPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errorMsg, setErrorMsg] = useState(''); // エラー表示用

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrorMsg(''); // 入力変更時にエラーを消す
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    try {
      // API連携: FastAPIの仕様(OAuth2Form)に合わせてデータを変換
      // usernameフィールドに email を渡すのがポイントです
      const params = new URLSearchParams();
      params.append('username', formData.email);
      params.append('password', formData.password);

      const response = await api.post('/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // 成功時: トークンを保存してカレンダーへ
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      console.log('Login successful');
      
      navigate('/calendar');

    } catch (error) {
      console.error('Login error:', error);
      if (error.response && error.response.status === 401) {
        setErrorMsg('メールアドレスまたはパスワードが間違っています。');
      } else {
        setErrorMsg('ログインに失敗しました。サーバーの状態を確認してください。');
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 bg-primary-600 text-white rounded-xl flex items-center justify-center text-2xl font-bold shadow-lg">
            G
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-slate-900">
          GeekCampにログイン
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          または{' '}
          <Link to="/signup" className="font-medium text-primary-600 hover:text-primary-500 transition-colors">
            新しいアカウントを作成
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/80 backdrop-blur-sm py-8 px-4 shadow sm:rounded-xl sm:px-10 border border-slate-200">
          
          {/* エラーメッセージ表示エリア */}
          {errorMsg && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
              {errorMsg}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* メールアドレス */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                メールアドレス
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full appearance-none rounded-md border border-slate-300 px-3 py-2 placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm transition-all"
                />
              </div>
            </div>

            {/* パスワード */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                パスワード
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full appearance-none rounded-md border border-slate-300 px-3 py-2 placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm transition-all"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-900">
                  ログイン状態を保持
                </label>
              </div>

              <div className="text-sm">
                {/* 以前のWarning対策: aタグをbuttonに変更 */}
                <button
                  type="button"
                  onClick={() => alert('パスワードリセット機能は現在開発中です')}
                  className="font-medium text-primary-600 hover:text-primary-500 bg-transparent border-none p-0 cursor-pointer"
                >
                  パスワードをお忘れですか？
                </button>
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-lg border border-transparent bg-primary-600 py-2.5 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all transform hover:scale-[1.02]"
              >
                ログイン
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SigninPage;