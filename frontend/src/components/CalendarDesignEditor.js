import React from 'react';

const CalendarDesignEditor = ({ settings, onUpdate }) => {

  // 汎用的な変更ハンドラ
  const handleChange = (key, value) => {
    // 親コンポーネントのstateを更新
    onUpdate({
      ...settings,
      [key]: value,
    });
  };

  // 画像アップロード用ハンドラ
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // ブラウザ上でプレビューするためのURLを生成
      const imageUrl = URL.createObjectURL(file);
      handleChange('backgroundImage', imageUrl);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. 背景色ピッカー */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          背景色
        </label>
        <div className="flex items-center gap-3">
          <input
            type="color"
            value={settings.backgroundColor}
            onChange={(e) => handleChange('backgroundColor', e.target.value)}
            className="h-10 w-20 p-1 border border-gray-300 rounded cursor-pointer"
          />
          <span className="text-gray-500 text-sm">{settings.backgroundColor}</span>
        </div>
      </div>

      {/* 2. 背景画像アップロード */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          背景画像 (任意)
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
        {settings.backgroundImage && (
          <button
            onClick={() => handleChange('backgroundImage', null)}
            className="mt-2 text-xs text-red-500 underline"
          >
            画像を削除して背景色に戻す
          </button>
        )}
      </div>

      {/* 3. フォント選択 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          フォントスタイル
        </label>
        <select
          value={settings.font}
          onChange={(e) => handleChange('font', e.target.value)}
          className="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="Arial">Arial (シンプル)</option>
          <option value="Times New Roman">Times New Roman (明朝体風)</option>
          <option value="Courier New">Courier New (タイプライター風)</option>
          <option value="Impact">Impact (太字)</option>
        </select>
      </div>

      {/* 4. レイアウト選択 (ラジオボタン) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          レイアウト
        </label>
        <div className="flex flex-col gap-2">
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="layout"
              value="standard"
              checked={settings.layout === 'standard'}
              onChange={(e) => handleChange('layout', e.target.value)}
              className="form-radio text-blue-600"
            />
            <span className="ml-2">スタンダード (中央配置)</span>
          </label>
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="layout"
              value="minimal"
              checked={settings.layout === 'minimal'}
              onChange={(e) => handleChange('layout', e.target.value)}
              className="form-radio text-blue-600"
            />
            <span className="ml-2">ミニマル (左寄せ)</span>
          </label>
        </div>
      </div>
      {/* 5. 文字色の変更 */}
<div className="mt-4">
  <label className="block text-sm font-medium text-gray-700 mb-2">
    文字の色
  </label>
  <div className="flex items-center gap-3">
    <input
      type="color"
      value={settings.textColor || '#000000'} // 初期値は黒
      onChange={(e) => handleChange('textColor', e.target.value)}
      className="h-10 w-20 p-1 border border-gray-300 rounded cursor-pointer"
    />
  </div>
</div>

{/* 6. 文字の位置（配置） */}
<div className="mt-4">
  <label className="block text-sm font-medium text-gray-700 mb-2">
    文字の位置
  </label>
  <div className="flex gap-2">
    {['start', 'center', 'end'].map((pos) => (
      <button
        key={pos}
        onClick={() => handleChange('textPosition', pos)}
        className={`px-3 py-1 border rounded ${
          settings.textPosition === pos 
            ? 'bg-blue-500 text-white border-blue-500' 
            : 'bg-white text-gray-700 border-gray-300'
        }`}
      >
        {pos === 'start' ? '上' : pos === 'center' ? '中央' : '下'}
      </button>
    ))}
  </div>
</div>      
      {/* 7.    タイトル入力 --- */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          カレンダーのタイトル
        </label>
        <input
          type="text"
          value={settings.title || ''}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="例: October 2023"
          className="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>




    </div>
  );
};

export default CalendarDesignEditor;
