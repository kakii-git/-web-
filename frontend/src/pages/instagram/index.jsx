// src/pages/instagram/index.jsx
import React, { useState } from 'react';

// 今後 features/instagram/components/ からインポートすることになります
import CalendarDesignEditor from '../../components/CalendarDesignEditor';
import CalendarImagePreview from '../../components/CalendarImagePreview';
const InstagramPage = () => {
  // Step 5: デザイン状態の連携
  const [designSettings, setDesignSettings] = useState({
    backgroundColor: '#ffffff',//初期設定
    font: 'Arial',
    layout: 'standard',
    backgroudImage: null,
    title: 'January 2026',
    fontSize: 18,
  });
  const handleDownload = () => {//ダウンロードの実装場所
    alert("ダウンロード機能はAPI連携の実装後に有効になります！");
  };
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800">Instagram用カレンダー作成</h1>
        <p className="text-gray-600">デザインを編集して画像をダウンロードできます</p>
      </header>

      <div className="flex flex-col lg:flex-row gap-8 max-w-6xl mx-auto">
        
        {/* 左側: エディタ (Step 3で実装予定) */}
        <div className="flex-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 border-b pb-2">デザイン編集</h2>
            <CalendarDesignEditor
              settings={designSettings}
              onUpdate={setDesignSettings}
            />
        </div>

        {/* 右側: プレビュー (Step 4で実装予定) */}
        <div className="flex-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 border-b pb-2">プレビュー</h2>
          <CalendarImagePreview
            settings={designSettings}
            onDownload={handleDownload}
          />
        </div>

      </div>
    </div>
  );
};

export default InstagramPage;
