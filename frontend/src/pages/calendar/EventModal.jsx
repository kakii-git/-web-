// frontend/src/pages/calendar/EventModal.jsx
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

const formatDate = (date) => {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleString('ja-JP', {
    month: 'long', day: 'numeric', weekday: 'short', hour: '2-digit', minute: '2-digit'
  });
};

const EventModal = ({ 
  isOpen, 
  onClose, 
  event, 
  readOnly = false, 
  isAdmin = false, // ▼ 追加
  onEdit = () => {}, // ▼ 追加
  currentUser = null, 
  onReactionUpdate = () => {} 
}) => {
  const [isMembersExpanded, setIsMembersExpanded] = useState(false);

  useEffect(() => {
    if (isOpen) setIsMembersExpanded(false);
  }, [isOpen]);

  if (!isOpen || !event) return null;

  const { title, start, end, extendedProps, backgroundColor } = event;
  const { description, location, groupName, task_user_relations } = extendedProps || {};

  // 自分のリアクション確認
  let myStatus = 'undecided';
  if (currentUser && task_user_relations) {
    const myRelation = task_user_relations.find(r => r.user_id === currentUser.user_id);
    if (myRelation) myStatus = myRelation.reaction;
  }

  // 参加メンバー抽出
  const joinedMembers = task_user_relations
    ? task_user_relations.filter(r => r.reaction === 'join' && r.user)
    : [];

  const INITIAL_DISPLAY_COUNT = 10;
  const hasMoreMembers = joinedMembers.length > INITIAL_DISPLAY_COUNT;
  const displayedMembers = isMembersExpanded ? joinedMembers : joinedMembers.slice(0, INITIAL_DISPLAY_COUNT);
  const remainingCount = joinedMembers.length - INITIAL_DISPLAY_COUNT;

  const modalContent = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="absolute inset-0 -z-10" onClick={onClose}></div>

      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200 relative z-10 max-h-[90vh] flex flex-col">
        
        {/* ヘッダー */}
        <div className="px-6 py-4 border-b border-slate-100 relative overflow-hidden shrink-0">
          <div className="absolute left-0 top-0 bottom-0 w-1.5" style={{ backgroundColor: backgroundColor || '#6366f1' }}></div>
          <div className="pl-2 pr-6"> {/* 右側に閉じるボタンなどのスペースを確保 */}
            {groupName && (
              <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold text-white mb-1" style={{ backgroundColor: backgroundColor || '#6366f1' }}>
                {groupName}
              </span>
            )}
            <h3 className="text-xl font-bold text-slate-900 leading-tight">{title}</h3>
            <p className="text-sm text-slate-500 mt-1 font-medium">{formatDate(start)} {end && ` - ${formatDate(end)}`}</p>
          </div>
          
          <div className="absolute top-4 right-4 flex gap-2">
            {/* ▼▼▼ 編集ボタン (管理者のみ) ▼▼▼ */}
            {!readOnly && isAdmin && (
              <button
                onClick={onEdit}
                className="text-slate-400 hover:text-indigo-600 p-1 rounded-full hover:bg-slate-100 transition-colors"
                title="編集する"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1">✕</button>
          </div>
        </div>

        {/* コンテンツ */}
        <div className="px-6 py-6 space-y-6 overflow-y-auto">
          {/* 場所 */}
          {location && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-400">📍</div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">場所</p>
                <p className="text-sm font-medium text-slate-800 mt-0.5">{location}</p>
              </div>
            </div>
          )}

          {/* 詳細 */}
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-400">📝</div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">詳細</p>
              <p className="text-sm text-slate-600 mt-0.5 whitespace-pre-wrap leading-relaxed">{description || '詳細はありません'}</p>
            </div>
          </div>

          {/* 参加メンバー表示 */}
          {!readOnly && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-400">👥</div>
              <div className="w-full">
                <div className="flex justify-between items-baseline">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    参加予定 ({joinedMembers.length})
                  </p>
                </div>
                
                {joinedMembers.length > 0 ? (
                  <div className="mt-2">
                    <div className="flex flex-wrap gap-2">
                      {displayedMembers.map((member) => (
                        <div key={member.user.user_id} className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-full pl-1 pr-3 py-1">
                          <div className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-[10px] font-bold">
                            {member.user.user_name ? member.user.user_name[0] : 'U'}
                          </div>
                          <span className="text-xs text-slate-700 font-medium">
                            {member.user.user_name}
                          </span>
                        </div>
                      ))}
                      {/* 省略バッジ */}
                      {!isMembersExpanded && hasMoreMembers && (
                        <div className="flex items-center justify-center bg-slate-100 text-slate-500 rounded-full px-3 py-1 text-xs font-bold border border-slate-200">+{remainingCount}名</div>
                      )}
                    </div>
                    {/* 展開ボタン */}
                    {hasMoreMembers && (
                      <button
                        onClick={() => setIsMembersExpanded(!isMembersExpanded)}
                        className="mt-3 text-xs font-bold text-indigo-600 hover:text-indigo-800 hover:underline flex items-center gap-1"
                      >
                        {isMembersExpanded ? '▲ 一覧を閉じる' : '▼ 全ての参加者を表示する'}
                      </button>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400 mt-1 italic">まだ参加表明はありません</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* フッター */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 shrink-0">
          {!readOnly ? (
            <div className="flex flex-col sm:flex-row justify-between items-center w-full gap-3">
              <div className="flex gap-2 w-full sm:w-auto">
                {myStatus === 'join' ? (
                  <>
                    <button className="px-4 py-2 text-sm font-bold rounded-md bg-green-100 text-green-700 border border-green-200 cursor-default">✓ 参加中</button>
                    <button onClick={() => onReactionUpdate(event.id, 'absent')} className="px-4 py-2 text-sm font-medium rounded-md bg-white text-slate-600 border border-slate-300 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors">欠席する</button>
                  </>
                ) : (
                  <button onClick={() => onReactionUpdate(event.id, 'join')} className="flex-1 sm:flex-none px-6 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-colors">参加する</button>
                )}
              </div>
              <button onClick={onClose} className="text-sm text-slate-500 hover:text-slate-800">閉じる</button>
            </div>
          ) : (
            <div className="flex justify-end">
              <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200 rounded-md">閉じる</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default EventModal;
