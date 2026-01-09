import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../lib/api'; // 作成したapi設定を読み込み

const SignupPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [errorMsg, setErrorMsg] = useState(''); // エラー表示用

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    try {
      // ------------------------------------------------
      // 1. 新規登録を実行
      // ------------------------------------------------
      const signupPayload = {
        user_name: formData.username,
        email: formData.email,
        password: formData.password
      };

      await api.post('/signup', signupPayload);
      console.log('登録成功。自動ログインを試みます...');

      // ------------------------------------------------
      // 2. そのままログイン（トークン取得）を実行
      // ------------------------------------------------
      // ログインには x-www-form-urlencoded 形式が必要なので変換
      const loginParams = new URLSearchParams();
      loginParams.append('username', formData.email); // username欄にemailを入れる仕様
      loginParams.append('password', formData.password);

      const loginResponse = await api.post('/token', loginParams, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // ------------------------------------------------
      // 3. トークン保存 & 画面遷移
      // ------------------------------------------------
      const { access_token } = loginResponse.data;
      localStorage.setItem('token', access_token);
      
      console.log('自動ログイン成功！');
      
      // アラートは出さずに、スムーズにカレンダーへ移動させる
      // (もしウェルカムメッセージを出したいなら、移動先のカレンダー画面で出すのが今風です)
      navigate('/calendar');

    } catch (error) {
      console.error('Signup/Login error:', error);
      
      if (error.response && error.response.data && error.response.data.detail) {
        const detail = error.response.data.detail;
        setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
      } else {
        setErrorMsg('登録または自動ログインに失敗しました。');
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
          アカウントを作成
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          <Link to="/signin" className="font-medium text-primary-600 hover:text-primary-500 transition-colors">
            すでにアカウントをお持ちの方はログイン
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
            {/* ユーザー名 */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-700">
                ユーザー名
              </label>
              <div className="mt-1">
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="block w-full appearance-none rounded-md border border-slate-300 px-3 py-2 placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm transition-all"
                  placeholder="例: geek_taro"
                />
              </div>
            </div>

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
                  placeholder="name@example.com"
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
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full appearance-none rounded-md border border-slate-300 px-3 py-2 placeholder-slate-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm transition-all"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-lg border border-transparent bg-primary-600 py-2.5 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all transform hover:scale-[1.02]"
              >
                アカウント登録
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;