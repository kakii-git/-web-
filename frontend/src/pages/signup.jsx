import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const SignupPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Signup attempt:', formData);
    // TODO: ここでAPI連携を行う
    // 仮の成功としてカレンダーへ遷移
    navigate('/calendar');
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          {/* ロゴ部分 */}
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