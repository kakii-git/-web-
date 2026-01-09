// frontend/src/pages/group/[groupId]/info/index.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../../../lib/api';

const GroupInfoPage = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();
  
  const [group, setGroup] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [copyStatus, setCopyStatus] = useState(''); // コピー完了メッセージ用

  useEffect(() => {
    fetchGroupInfo();
  }, [groupId]);

  const fetchGroupInfo = async () => {
    try {
      // 既存API(/me/groups)からグループ情報を探して表示します
      const response = await api.get('/me/groups');
      const targetGroup = response.data.find(g => g.group_id === groupId);
      
      if (targetGroup) {
        setGroup(targetGroup);
        setIsAdmin(targetGroup.is_representative);
      } else {
        alert('グループ情報が見つかりませんでした。');
        navigate('/calendar');
      }
    } catch (error) {
      console.error("Failed to fetch group info:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // --- 個別コピー機能 ---
  const handleCopy = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus(`${label}をコピーしました`);
      setTimeout(() => setCopyStatus(''), 2000);
    } catch (err) {
      setCopyStatus('コピーに失敗しました');
    }
  };

  // --- 招待テキスト一括コピー機能 ---
  const handleCopyInvite = async () => {
    if (!group) return;
    
    // LINE等に貼り付けやすい形式を作成
    const text = `グループへの招待です！\n\nグループ名：${group.group_name}\nグループID：${group.group_id}\n\nアプリの「グループに参加」画面で入力してください。`;
    
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus('招待用テキストをコピーしました');
      setTimeout(() => setCopyStatus(''), 2000);
    } catch (err) {
      setCopyStatus('コピーに失敗しました');
    }
  };

  // --- グループ脱退 (全メンバー) ---
  const handleLeaveGroup = async () => {
    if (!window.confirm('本当にグループから脱退しますか？\nこのグループの予定は見られなくなります。')) return;
    
    try {
      // 自分のユーザーIDが必要なため、一度/meを叩いて取得
      const meRes = await api.get('/me');
      const myUserId = meRes.data.user_id;

      // メンバー削除APIを実行 (自分自身を指定)
      await api.delete(`/groups/${groupId}/members/${myUserId}`);
      
      alert('グループから脱退しました。');
      navigate('/calendar');
    } catch (error) {
      console.error("Leave failed:", error);
      alert('脱退に失敗しました。管理者は脱退できない場合があります（その場合は解散してください）。');
    }
  };

  // --- グループ解散 (管理者のみ) ---
  const handleDeleteGroup = async () => {
    if (!window.confirm('本当にグループを解散しますか？\nこの操作は取り消せません。\n全てのタスクとメンバー情報が削除されます。')) return;
    try {
      await api.delete(`/groups/${groupId}`);
      alert('グループを解散しました。');
      navigate('/calendar');
    } catch (error) {
      alert('解散に失敗しました。');
    }
  };

  if (isLoading) return <div className="p-8 text-center text-slate-500">読み込み中...</div>;
  if (!group) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in duration-300">
      
      {/* 1. 招待情報エリア */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h1 className="text-xl font-bold text-slate-900 mb-6">
          メンバー招待
        </h1>

        {copyStatus && (
          <div className="mb-4 p-3 bg-green-50 text-green-700 text-sm rounded-md border border-green-200 text-center font-bold">
            {copyStatus}
          </div>
        )}

        <div className="space-y-4">
          {/* グループ名 */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              グループ名
            </label>
            <div className="flex gap-2">
              <div className="flex-1 bg-slate-50 px-4 py-3 rounded-lg border border-slate-200 text-slate-900 font-bold select-all">
                {group.group_name}
              </div>
              <button
                onClick={() => handleCopy(group.group_name, 'グループ名')}
                className="px-4 py-2 bg-white border border-slate-300 text-slate-600 font-medium rounded-lg hover:bg-slate-50 shadow-sm transition-colors text-sm"
              >
                コピー
              </button>
            </div>
          </div>

          {/* グループID */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              グループID
            </label>
            <div className="flex gap-2">
              <div className="flex-1 bg-slate-50 px-4 py-3 rounded-lg border border-slate-200 text-slate-600 font-mono text-sm select-all">
                {group.group_id}
              </div>
              <button
                onClick={() => handleCopy(group.group_id, 'グループID')}
                className="px-4 py-2 bg-white border border-slate-300 text-slate-600 font-medium rounded-lg hover:bg-slate-50 shadow-sm transition-colors text-sm"
              >
                コピー
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-slate-100">
          <button
            onClick={handleCopyInvite}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-sm transition-colors flex items-center justify-center"
          >
            まとめてコピーする
          </button>
          <p className="text-center text-xs text-slate-400 mt-2">
            招待用メッセージ全文をクリップボードにコピーします
          </p>
        </div>
      </div>

      {/* 2. グループ設定・アクションエリア */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-6">
          設定・操作
        </h2>

        <div className="space-y-6">
          
          {/* グループ脱退 (全ユーザー) */}
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div>
              <p className="text-sm font-bold text-slate-700">グループから脱退</p>
              <p className="text-xs text-slate-500 mt-0.5">このグループの予定は見られなくなります</p>
            </div>
            <button
              onClick={handleLeaveGroup}
              className="px-4 py-2 bg-white border border-slate-300 text-slate-600 font-bold rounded-lg hover:bg-slate-200 transition-colors shadow-sm text-sm"
            >
              脱退する
            </button>
          </div>

          {/* グループ解散 (管理者のみ) */}
          {isAdmin && (
            <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-100">
              <div>
                <p className="text-sm font-bold text-red-800">グループの解散</p>
                <p className="text-xs text-red-600 mt-0.5">全てのデータが削除されます</p>
              </div>
              <button
                onClick={handleDeleteGroup}
                className="px-4 py-2 bg-white border border-red-200 text-red-600 font-bold rounded-lg hover:bg-red-600 hover:text-white transition-colors shadow-sm text-sm"
              >
                解散する
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default GroupInfoPage;