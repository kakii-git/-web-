// frontend/src/pages/tasks/index.jsx
import React, { useState, useEffect } from 'react';
// import { Link } from 'react-router-dom'; // リンクを使わないので削除
import api from '../../lib/api';

export default function TasksListPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 現在の日時から初期表示する年月を設定
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1; // 0-indexed -> 1-12

  useEffect(() => {
    fetchTasks();
  }, [year, month]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      // グループ横断の自分用タスクを取得 (GET /my-tasks)
      const response = await api.get('/my-tasks', {
        params: { year, month }
      });
      setTasks(response.data);
    } catch (err) {
      console.error('タスク取得エラー:', err);
      setError('タスクの取得に失敗しました。');
    } finally {
      setLoading(false);
    }
  };

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 2, 1)); // 前月へ
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month, 1)); // 翌月へ
  };

  // 日付フォーマット用関数
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', { day: 'numeric', weekday: 'short' });
  };

  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">自分のタスク一覧</h1>
        <div className="flex items-center space-x-4">
          <button 
            onClick={handlePrevMonth}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            &lt; 前月
          </button>
          <span className="text-xl font-semibold">
            {year}年 {month}月
          </span>
          <button 
            onClick={handleNextMonth}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            翌月 &gt;
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10">読み込み中...</div>
      ) : error ? (
        <div className="text-red-500 text-center py-10">{error}</div>
      ) : tasks.length === 0 ? (
        <div className="text-gray-500 text-center py-10">
          この月のタスク・予定はありません。
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {tasks.map((task) => (
              /* hoverエフェクトを削除し、単なるリスト表示に変更 */
              <li key={task.task_id} className="bg-white">
                {/* Linkタグをdivに変更して遷移を無効化 */}
                <div className="block p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-start gap-4">
                      {/* 日付・時間 */}
                      <div className="text-center min-w-[3.5rem]">
                        <div className="text-lg font-bold text-gray-700">
                          {formatDate(task.date)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {task.time_span_begin ? formatTime(task.time_span_begin) : '終日'}
                        </div>
                      </div>
                      
                      {/* タスク情報 */}
                      <div>
                        <div className="text-sm text-gray-500 mb-1">
                          {task.group_name}
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {task.title}
                        </h3>
                        {task.location && (
                          <div className="text-sm text-gray-600 mt-1">
                            📍 {task.location}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* 右側の矢印(>)アイコンは遷移を示唆するため削除しました */}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}