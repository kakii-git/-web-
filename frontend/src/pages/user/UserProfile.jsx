import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
// ファイル位置が src/pages/user/UserProfile.jsx なので、
// src/lib/api.js へのパスは ../../lib/api になります
import api from '../../lib/api';

const UserProfilePage = () => {
  const { userId } = useParams(); // URLの :userId (例: "me")
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      try {
        // "me" なら自分の情報、それ以外ならそのIDのユーザー情報を取得
        // 現時点ではバックエンドに合わせて /me を使用
        const endpoint = userId === 'me' ? '/me' : '/me'; 
        
        const response = await api.get(endpoint);
        setUser(response.data);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchUser();
    }
  }, [userId]);

  return (
    <div className="max-w-3xl mx-auto py-4">
      <h1 className="text-2xl font-bold text-slate-900 mb-8">
        {userId === 'me' ? 'マイページ' : 'ユーザープロフィール'}
      </h1>
      
      {loading ? (
        <div className="p-4 text-slate-500 animate-pulse">情報を取得中...</div>
      ) : user ? (
        <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
          {/* プロフィールヘッダー */}
          <div className="bg-white px-6 py-6 border-b border-slate-100 flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center text-2xl font-bold text-primary-600">
              {user.user_name ? user.user_name[0].toUpperCase() : 'U'}
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800">{user.user_name}</h2>
              <p className="text-sm text-slate-500">{user.email}</p>
            </div>
          </div>

          {/* 詳細リスト */}
          <div className="divide-y divide-slate-100">
            <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-3 gap-4 hover:bg-slate-50 transition-colors">
              <dt className="text-sm font-medium text-slate-500">ユーザー名</dt>
              <dd className="text-sm text-slate-900 sm:col-span-2 font-medium">{user.user_name}</dd>
            </div>

            <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-3 gap-4 hover:bg-slate-50 transition-colors">
              <dt className="text-sm font-medium text-slate-500">メールアドレス</dt>
              <dd className="text-sm text-slate-900 sm:col-span-2">{user.email}</dd>
            </div>

            <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-3 gap-4 hover:bg-slate-50 transition-colors">
              <dt className="text-sm font-medium text-slate-500">ユーザーID</dt>
              <dd className="text-sm text-slate-600 sm:col-span-2 font-mono bg-slate-100 px-2 py-1 rounded inline-block w-fit">
                {user.user_id}
              </dd>
            </div>

            <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-3 gap-4 hover:bg-slate-50 transition-colors">
              <dt className="text-sm font-medium text-slate-500">アカウント作成日</dt>
              <dd className="text-sm text-slate-900 sm:col-span-2">
                {user.created_at ? new Date(user.created_at).toLocaleDateString('ja-JP') : '-'}
              </dd>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-slate-500">
          ユーザーが見つかりませんでした。
        </div>
      )}
    </div>
  );
};

export default UserProfilePage;