// frontend/src/pages/group/join/index.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../../lib/api';

const GroupJoinPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    group_id: '',
    group_name: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // 既存API: POST /groups/join
      // { group_id, group_name } が必要
      await api.post('/groups/join', formData);
      
      alert('参加リクエストを送信しました。\n管理者の承認をお待ちください。');
      navigate('/calendar'); // マイページへ戻る
    } catch (error) {
      console.error("Join failed:", error);
      // エラーメッセージを詳細に出す
      if (error.response && error.response.data && error.response.data.detail) {
        alert(`エラー: ${error.response.data.detail}`);
      } else {
        alert('参加リクエストの送信に失敗しました。IDと名前が正しいか確認してください。');
      }
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-xl shadow-sm border border-slate-200">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">グループに参加</h1>
      <p className="text-sm text-slate-500 mb-6">
        管理者から共有された「グループID」と「グループ名」を入力してください。
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">グループID (UUID)</label>
          <input
            type="text"
            required
            value={formData.group_id}
            onChange={(e) => setFormData({...formData, group_id: e.target.value})}
            className="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-3 py-2 border font-mono text-sm"
            placeholder="例: 123e4567-e89b-..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">グループ名</label>
          <input
            type="text"
            required
            value={formData.group_name}
            onChange={(e) => setFormData({...formData, group_name: e.target.value})}
            className="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-3 py-2 border"
            placeholder="正確なグループ名を入力"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
          >
            リクエスト送信
          </button>
        </div>
      </form>
    </div>
  );
};

export default GroupJoinPage;