import React from 'react';

const CalendarImagePreview = ({ settings, onDownload }) => {
  // プレビュー表示用のスタイルを作成
  const previewStyle = {
    backgroundImage: settings.backgroundImage ? `url(${settings.backgroundImage})` : 'none',
    backgroundColor: settings.backgroundImage ? 'transparent' : settings.backgroundColor,
    fontFamily: settings.font,
    justifyContent: settings.textPosition || 'center', // 上・中・下の配置
    alignItems: 'center',
  };

  const textStyle = {
    fontSize: `${settings.fontSize}px`,
    color: settings.textColor,
    textShadow: '0px 2px 4px rgba(0,0,0,0.3)',
    lineHeight: 1.2,
  };

  return (
    <div className="space-y-4">
      {/* プレビューエリア */}
      <div 
        className="rounded h-96 shadow-inner flex flex-col p-6 bg-center bg-cover transition-all duration-300 border border-gray-200"
        style={previewStyle}
      >
        <div className="text-center mx-auto max-w-full">
          {/* メインタイトル */}
          <h3 className="font-bold break-words whitespace-pre-wrap" style={textStyle}>
             {settings.title}
          </h3>
          
        </div>
      </div>

      {/* アクションボタンエリア */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onDownload}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-full shadow-lg transform transition hover:scale-105 flex items-center gap-2"
        >
          {/* ダウンロードアイコン (SVG) */}
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          画像をダウンロード
        </button>
      </div>
      
      <p className="text-xs text-center text-gray-500">
        ※現在はプレビューです。ボタンを押すと画像の生成・保存処理が走ります(次回以降実装)。
      </p>
    </div>
  );
};

export default CalendarImagePreview;
