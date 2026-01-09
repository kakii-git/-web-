import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../../lib/api';

const GroupCreatePage = () => {
  const navigate = useNavigate();
  const [groupName, setGroupName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!groupName.trim()) return;

    setIsLoading(true);
    try {
      // 既存API: POST /groups/
      // バックエンドの GroupCreate スキーマは { group_name: str } です
      const response = await api.post('/groups/', { group_name: groupName });
      
      const newGroupId = response.data.group_id;
      alert(`グループ「${response.data.group_name}」を作成しました！`);
      
      // 作成されたグループのカレンダーへ移動
      navigate(`/group/${newGroupId}`);
    } catch (error) {
      console.error("Create group failed:", error);
      alert('グループの作成に失敗しました。');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-xl shadow-sm border border-slate-200">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">新しいグループを作成</h1>
      <p className="text-sm text-slate-500 mb-6">あなたが管理者となり、新しいグループを立ち上げます。</p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            グループ名
          </label>
          <input
            type="text"
            required
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            className="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-3 py-2 border"
            placeholder="例: 開発チームA"
          />
        </div>

        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-lg"
          >
            キャンセル
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm disabled:opacity-50"
          >
            {isLoading ? '作成中...' : '作成する'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default GroupCreatePage;