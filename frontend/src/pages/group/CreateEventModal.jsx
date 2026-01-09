// frontend/src/pages/group/CreateEventModal.jsx
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

const COLORS = [
  { value: '#6366f1', label: 'Indigo' },
  { value: '#ef4444', label: 'Red' },
  { value: '#f97316', label: 'Orange' },
  { value: '#eab308', label: 'Yellow' },
  { value: '#22c55e', label: 'Green' },
  { value: '#3b82f6', label: 'Blue' },
  { value: '#a855f7', label: 'Purple' },
  { value: '#ec4899', label: 'Pink' },
  { value: '#64748b', label: 'Slate' },
];

const CreateEventModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  initialDate, 
  initialStartTime,
  initialData = null // 編集用の初期データ
}) => {
  const isEditMode = !!initialData; // データがあれば編集モード

  const [formData, setFormData] = useState({
    title: '',
    date: '',
    startTime: '',
    endTime: '',
    location: '',
    description: '',
    color: '#6366f1',
    colorLabel: ''
  });

  // モーダルが開いたときの初期値セット
  useEffect(() => {
    if (isOpen) {
      if (isEditMode) {
        // 編集モード: 既存データをセット
        setFormData({
          title: initialData.title || '',
          date: initialData.date || '',
          startTime: initialData.startTime || '09:00',
          endTime: initialData.endTime || calculateEndTime(initialData.startTime || '09:00'),
          location: initialData.location || '',
          description: initialData.description || '',
          color: initialData.color || '#6366f1',
          colorLabel: initialData.colorLabel || ''
        });
      } else {
        // 新規作成モード: デフォルト値をセット
        setFormData(prev => ({
          ...prev,
          title: '',
          date: initialDate || '',
          startTime: initialStartTime || '09:00',
          endTime: calculateEndTime(initialStartTime || '09:00'),
          location: '',
          description: '',
          color: '#6366f1',
          colorLabel: ''
        }));
      }
    }
  }, [isOpen, initialDate, initialStartTime, initialData, isEditMode]);

  // 開始時間から+1時間を計算するヘルパー
  const calculateEndTime = (startStr) => {
    if (!startStr) return '';
    const [h, m] = startStr.split(':').map(Number);
    const date = new Date();
    date.setHours(h, m);
    date.setHours(date.getHours() + 1);
    return date.toTimeString().slice(0, 5);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prev => {
      const newData = { ...prev, [name]: value };
      if (name === 'startTime' && !isEditMode) { 
        // 新規作成時のみ、開始時間変更で終了時間を連動させる(編集時は勝手に変わると不便なため)
        newData.endTime = calculateEndTime(value);
      }
      return newData;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // [修正] endTimeが空文字の場合は無理にTをつけて結合せず、nullを渡す
    const startStr = formData.startTime ? `${formData.date}T${formData.startTime}` : null;
    const endStr = formData.endTime ? `${formData.date}T${formData.endTime}` : null;

    const submitPayload = {
      title: formData.title,
      start: startStr,
      end: endStr,
      location: formData.location,
      description: formData.description,
    };

    onSubmit(submitPayload);
    // 閉じるのは親側の制御に任せるか、ここで閉じるか。現状の実装ではonSubmit内でAPIコール後に閉じる想定ではない場合もあるが、
    // index.jsxではAPI成功後に閉じています。
    // エラーハンドリングのために、ここでは閉じずに親に任せるのが一般的ですが、
    // 元のコードに合わせて onCloseは呼ばないでおきます（index.jsx側で閉じています）。
    // もし親側で閉じる処理がないなら onClose() が必要です。
    // 今回の index.jsx では handleFormSubmit 成功時に setIsCreateModalOpen(false) しているのでOK。
  };

  if (!isOpen) return null;

  const modalContent = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="absolute inset-0 -z-10" onClick={onClose}></div>

      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200 relative z-10 flex flex-col max-h-[90vh]">
        
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 shrink-0">
          <h3 className="text-lg font-bold text-slate-800">
            {isEditMode ? 'タスクを編集' : '新規予定を作成'}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto">
          {/* タイトル */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">タイトル <span className="text-red-500">*</span></label>
            <input
              type="text"
              name="title"
              required
              autoFocus={!isEditMode}
              className="w-full rounded-lg border-slate-300 px-3 py-2.5 focus:border-indigo-500 focus:ring-indigo-500 font-bold text-slate-900 placeholder:font-normal"
              placeholder="タイトルを入力"
              value={formData.title}
              onChange={handleChange}
            />
          </div>

          {/* カラー設定 (実装中) */}
          <div className="opacity-50 pointer-events-none relative">
            <div className="absolute -top-1 right-0 bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-0.5 rounded border border-slate-200">
              ※ 現在開発中です
            </div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">カラー設定</label>
            <div className="flex flex-wrap gap-3 items-center">
              {COLORS.map((c) => (
                <div
                  key={c.value}
                  className={`w-8 h-8 rounded-full border-2 border-transparent`}
                  style={{ backgroundColor: c.value }}
                />
              ))}
              <input type="text" disabled placeholder="ラベル" className="ml-2 flex-1 rounded-md border-slate-300 text-sm py-1.5 px-3 bg-slate-50" />
            </div>
          </div>

          {/* 日時入力 */}
          <div className="grid grid-cols-12 gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
            <div className="col-span-12 sm:col-span-6">
              <label className="block text-xs font-bold text-slate-500 mb-1">日付</label>
              <input
                type="date"
                name="date"
                required
                className="w-full rounded-md border-slate-300 text-sm"
                value={formData.date}
                onChange={handleChange}
              />
            </div>
            <div className="col-span-6 sm:col-span-3">
              <label className="block text-xs font-bold text-slate-500 mb-1">開始</label>
              <input
                type="time"
                name="startTime"
                required
                step="300"
                className="w-full rounded-md border-slate-300 text-sm"
                value={formData.startTime}
                onChange={handleChange}
              />
            </div>
            <div className="col-span-6 sm:col-span-3">
              <label className="block text-xs font-bold text-slate-500 mb-1">終了</label>
              <input
                type="time"
                name="endTime"
                step="300"
                className="w-full rounded-md border-slate-300 text-sm"
                value={formData.endTime}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* 場所 */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">場所</label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-slate-400">📍</span>
              <input
                type="text"
                name="location"
                className="w-full rounded-md border-slate-300 pl-9 py-2 text-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="場所を入力"
                value={formData.location}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* 詳細 */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">詳細・メモ</label>
            <textarea
              name="description"
              rows="3"
              className="w-full rounded-md border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="詳細を記入"
              value={formData.description}
              onChange={handleChange}
            />
          </div>
        </form>

        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3 shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-200 rounded-lg transition-colors"
          >
            キャンセル
          </button>
          <button
            onClick={handleSubmit}
            className="px-6 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition-colors flex items-center gap-2"
          >
            <span>{isEditMode ? '更新する' : '作成する'}</span>
          </button>
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default CreateEventModal;