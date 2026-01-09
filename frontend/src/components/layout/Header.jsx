// frontend/src/components/layout/Header.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../lib/api';

export const Header = () => {
  const [isGroupMenuOpen, setIsGroupMenuOpen] = useState(false);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  
  // ▼ 追加: APIから取得したグループ一覧を管理
  const [groups, setGroups] = useState([]);
  
  const navigate = useNavigate();

  // ▼ 追加: メニューを開いた時（またはマウント時）に最新のグループ一覧を取得
  useEffect(() => {
    const fetchMyGroups = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;

        // 修正: バックエンドの現状に合わせて /users を削除
        const response = await api.get('/me/groups');
        setGroups(response.data);
      } catch (error) {
        console.error("Failed to fetch groups:", error);
      }
    };

    fetchMyGroups();
  }, [isGroupMenuOpen]); // メニューを開くたびに再取得してリストを最新化

  const handleGroupClick = (groupId) => {
    setIsGroupMenuOpen(false);
    navigate(`/group/${groupId}`);
  };

  const handleLogoutClick = () => {
    setIsLogoutModalOpen(true);
  };

  const confirmLogout = () => {
    localStorage.removeItem('token'); 
    setIsLogoutModalOpen(false);
    navigate('/signin');
  };

  return (
    <>
      <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="h-full px-6 max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/calendar" className="flex items-center gap-2 group">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-md flex items-center justify-center font-bold text-lg shadow-sm group-hover:bg-primary-700 transition-colors">G</div>
              <span className="text-lg font-bold text-slate-800 tracking-tight group-hover:text-primary-700 transition-colors">GeekCamp</span>
            </Link>
            
            <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-slate-600">
              <Link to="/calendar" className="px-3 py-2 rounded-md hover:bg-slate-50 hover:text-primary-600 transition-colors">マイカレンダー</Link>
              
              {/* グループメニュー */}
              <div className="relative">
                <button 
                  onClick={() => setIsGroupMenuOpen(!isGroupMenuOpen)} 
                  className={`flex items-center gap-1 px-3 py-2 rounded-md transition-colors ${isGroupMenuOpen ? 'bg-slate-100 text-primary-700' : 'hover:bg-slate-50 hover:text-primary-600'}`}
                >
                  参加グループ <span className="text-[10px] opacity-60">▼</span>
                </button>
                
                {isGroupMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsGroupMenuOpen(false)} />
                    <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-slate-100 py-1 z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                      
                      {/* グループリストエリア */}
                      <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200">
                        {groups.length > 0 ? (
                          groups.map((group) => (
                            <button 
                              key={group.group_id} 
                              onClick={() => handleGroupClick(group.group_id)} 
                              className="w-full text-left px-4 py-3 text-sm text-slate-700 hover:bg-slate-50 border-b border-slate-50 last:border-0 transition-colors group"
                            >
                              <div className="font-bold group-hover:text-indigo-600 transition-colors">{group.group_name}</div>
                              {group.is_representative && (
                                <span className="inline-block mt-1 text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded border border-yellow-200">管理者</span>
                              )}
                            </button>
                          ))
                        ) : (
                          <div className="px-4 py-6 text-xs text-slate-400 text-center">
                            参加しているグループはありません
                          </div>
                        )}
                      </div>

                      {/* ▼▼▼ 追加: アクションボタンエリア ▼▼▼ */}
                      <div className="bg-slate-50 border-t border-slate-100 p-2 space-y-1">
                        <button
                          onClick={() => {
                            setIsGroupMenuOpen(false);
                            navigate('/groups/new');
                          }}
                          className="flex items-center gap-2 w-full px-3 py-2 text-sm font-bold text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                        >
                          <span className="w-5 h-5 flex items-center justify-center bg-indigo-100 rounded-full text-xs">＋</span>
                          新規グループ作成
                        </button>
                        
                        <button
                          onClick={() => {
                            setIsGroupMenuOpen(false);
                            navigate('/groups/join');
                          }}
                          className="flex items-center gap-2 w-full px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200 rounded-md transition-colors"
                        >
                          <span className="w-5 h-5 flex items-center justify-center bg-slate-200 rounded-full text-xs">→</span>
                          グループに参加
                        </button>
                      </div>

                    </div>
                  </>
                )}
              </div>
              <Link to="/instagram" className="px-3 py-2 rounded-md hover:bg-slate-50 hover:text-primary-600 transition-colors">画像生成</Link>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <Link to="/user/me/profile" className="text-sm font-medium text-slate-600 hover:text-primary-600 flex items-center gap-2 px-3 py-1.5 rounded-full hover:bg-slate-50">
              <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">U</div>
              <span>Profile</span>
            </Link>

            <button
              onClick={handleLogoutClick}
              className="text-xs font-medium text-slate-400 hover:text-red-500 transition-colors px-2 py-1"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      {isLogoutModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/20 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm text-center animate-in zoom-in-95 duration-200">
            <h3 className="text-lg font-semibold text-slate-900">ログアウトしますか？</h3>
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setIsLogoutModalOpen(false)}
                className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium"
              >
                キャンセル
              </button>
              <button
                onClick={confirmLogout}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-bold shadow-sm"
              >
                ログアウト
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};