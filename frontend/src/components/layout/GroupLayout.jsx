import React from 'react';
import { Outlet, NavLink, useParams } from 'react-router-dom';
import { Header } from './Header';

export const GroupLayout = () => {
  const { groupId } = useParams();

  const menuItems = [
    { label: '予定表', path: `/group/${groupId}` },
    { label: 'メンバー一覧', path: `/group/${groupId}/members` },
    { label: '参加リクエスト管理', path: `/group/${groupId}/join_requests` },
    { label: 'グループ情報', path: `/group/${groupId}/info` },
  ];

  return (
    // bg-gray-50 を削除しました
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1 max-w-7xl mx-auto w-full">
        {/* 左サイドバー */}
        <aside className="w-64 bg-white/80 backdrop-blur-sm border-r border-slate-200 hidden md:block">
          <div className="p-6 sticky top-16">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Group Menu
            </h2>
            <nav className="space-y-1">
              {menuItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === `/group/${groupId}`}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </aside>
        {/* コンテンツエリア */}
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};