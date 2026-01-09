// frontend/src/pages/group/[groupId]/index.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import api from '../../../lib/api';

import EventModal from '../../calendar/EventModal';
import CreateEventModal from '../CreateEventModal';

const GroupCalendarPage = () => {
  const { groupId } = useParams();
  
  const [events, setEvents] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  // 新規作成用初期値
  const [initialDateStr, setInitialDateStr] = useState('');
  const [initialStartTimeStr, setInitialStartTimeStr] = useState('');
  
  // 編集用データ (これがセットされていると編集モードになる)
  const [editTargetData, setEditTargetData] = useState(null);

  // 1. 権限チェック
  useEffect(() => {
    const fetchUserStatus = async () => {
      try {
        const [meRes, membersRes] = await Promise.all([
          api.get('/me'),
          api.get(`/groups/${groupId}/members`)
        ]);

        const myUser = meRes.data;
        setCurrentUser(myUser);

        const myMembership = membersRes.data.find(m => {
          if (m.user_id === myUser.user_id) return true;
          if (m.user && m.user.user_id === myUser.user_id) return true;
          return false;
        });

        setIsAdmin(myMembership && myMembership.is_representative === true);
      } catch (error) {
        console.error("Auth check failed:", error);
      }
    };
    if (groupId) fetchUserStatus();
  }, [groupId]);

  // 2. タスク取得
  const fetchTasks = useCallback(async () => {
    try {
      const response = await api.get(`/groups/${groupId}/tasks`);
      const mappedEvents = response.data.map(task => ({
        id: task.task_id,
        title: task.title,
        start: task.time_span_begin || task.date, 
        end: task.time_span_end,
        color: '#6366f1',
        extendedProps: {
          groupName: 'Current Group', 
          location: task.location,
          description: task.description,
          task_id: task.task_id,
          task_user_relations: task.task_user_relations || [],
          // [修正] ステータス情報を追加
          status: task.status,
          is_task: task.is_task
        }
      }));
      setEvents(mappedEvents);
    } catch (error) {
      console.error("Fetch tasks failed:", error);
    }
  }, [groupId]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // --- イベントハンドラ ---

  // カレンダーの日付クリック
  const handleDateSelect = (selectInfo) => {
    if (!isAdmin) return;
    setEditTargetData(null); // 編集データをクリア
    setInitialDateStr(selectInfo.startStr);
    setInitialStartTimeStr('09:00');
    setIsCreateModalOpen(true);
  };

  // イベントクリック (詳細表示)
  const handleEventClick = (info) => {
    const eventObj = {
      id: info.event.id,
      title: info.event.title,
      start: info.event.start,
      end: info.event.end,
      backgroundColor: info.event.backgroundColor,
      extendedProps: info.event.extendedProps
    };
    setSelectedEvent(eventObj);
    setIsDetailModalOpen(true);
  };

  // 詳細モーダル内の「編集」ボタンクリック
  const handleEditClick = () => {
    if (!selectedEvent) return;
    
    // イベントオブジェクトから編集用データ形式へ変換
    const { start, end, extendedProps, title } = selectedEvent;
    
    // 日付 (YYYY-MM-DD)
    const dateStr = start.toISOString().split('T')[0];
    
    // 時間 (HH:mm) - start
    const startH = String(start.getHours()).padStart(2, '0');
    const startM = String(start.getMinutes()).padStart(2, '0');
    
    // 時間 (HH:mm) - end
    let endStr = '';
    if (end) {
      const endH = String(end.getHours()).padStart(2, '0');
      const endM = String(end.getMinutes()).padStart(2, '0');
      endStr = `${endH}:${endM}`;
    }

    setEditTargetData({
      id: selectedEvent.id, // 更新時に使うID
      title: title,
      date: dateStr,
      startTime: `${startH}:${startM}`,
      endTime: endStr,
      location: extendedProps.location,
      description: extendedProps.description,
      // [修正] 既存のステータスと種別を引き継ぐ
      status: extendedProps.status,
      is_task: extendedProps.is_task
    });

    setIsDetailModalOpen(false); // 詳細を閉じる
    setIsCreateModalOpen(true);  // 編集(作成)モーダルを開く
  };

  // ドラッグ＆ドロップ更新
  const handleEventDrop = async (info) => {
    if (!isAdmin) {
      info.revert();
      return;
    }
    
    // 誤操作防止の確認
    if (!window.confirm(`「${info.event.title}」の日程を変更しますか？`)) {
      info.revert();
      return;
    }

    try {
      // 1. 新しい日程情報の抽出
      // FullCalendarのイベントオブジェクトから日時を取得
      const { start, end, allDay } = info.event;
      
      // ISO文字列生成 (YYYY-MM-DDTHH:mm:ss)
      const newStartISO = start ? start.toISOString() : null;
      const newEndISO = end ? end.toISOString() : null;
      
      // YYYY-MM-DD形式
      const newDateStr = start ? start.toISOString().split('T')[0] : null;

      // 2. 既存データの引継ぎ
      // PUTリクエストなので、変更しないフィールドも全て送信しないと消える可能性がある
      const props = info.event.extendedProps;
      
      const payload = {
        title: info.event.title,
        location: props.location || "",
        description: props.description || "",
        
        // ステータス等の維持
        is_task: props.is_task !== undefined ? props.is_task : true,
        status: props.status || "未着手",
        
        // 日時情報の構築
        time_span_begin: null,
        time_span_end: null,
        date: undefined
      };

      // 3. ロジック分岐: 終日(AllDay)か、時間指定か
      if (allDay) {
        // --- 終日スロットへドロップした場合 ---
        // 時間情報はNullにし、dateを設定する
        payload.date = newDateStr;
        payload.time_span_begin = null;
        payload.time_span_end = null;
      } else {
        // --- 時間スロットへドロップした場合 ---
        // dateをundefined(送信しない)にし、時間を設定する
        // ※バックエンドの仕様に合わせて undefined を使う
        payload.date = undefined;
        payload.time_span_begin = newStartISO;
        payload.time_span_end = newEndISO;
      }
      
      // undefinedのキーを削除（念のため）
      Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);

      console.log("Drop Update Payload:", payload);

      // 4. API送信
      await api.put(`/groups/${groupId}/tasks/${info.event.id}`, payload);
      
      // 成功したら見た目はFullCalendarが自動更新済みなのでそのままでOK
      // ただし念のため裏で再取得しても良い
      // fetchTasks(); 

    } catch (error) {
      console.error("Update failed:", error);
      
      // エラー詳細の表示
      let errorMsg = "更新に失敗しました";
      if (error.response?.data?.detail) {
        errorMsg += `\n${JSON.stringify(error.response.data.detail)}`;
      }
      alert(errorMsg);
      
      // 失敗した場合はカレンダー上の表示を元に戻す
      info.revert();
    }
  };

  // 新規作成ボタン
  const handleOpenCreateModal = () => {
    setEditTargetData(null); // 編集データをクリア
    const now = new Date();
    const nextHour = new Date(now);
    nextHour.setHours(now.getHours() + 1);
    nextHour.setMinutes(0, 0, 0);

    const dateStr = nextHour.getFullYear() + '-' + 
      String(nextHour.getMonth() + 1).padStart(2, '0') + '-' + 
      String(nextHour.getDate()).padStart(2, '0');
    
    const timeStr = String(nextHour.getHours()).padStart(2, '0') + ':' + 
      String(nextHour.getMinutes()).padStart(2, '0');

    setInitialDateStr(dateStr);
    setInitialStartTimeStr(timeStr);
    setIsCreateModalOpen(true);
  };

  // フォーム送信 (新規作成 or 更新)
  const handleFormSubmit = async (formData) => {
    try {
      // 1. 時間文字列の整形 (ISO 8601形式: YYYY-MM-DDTHH:mm:ss)
      const startTimeISO = formData.start && formData.start.includes('T') 
        ? (formData.start.length === 16 ? `${formData.start}:00` : formData.start)
        : null;

      const endTimeISO = formData.end && formData.end.includes('T')
        ? (formData.end.length === 16 ? `${formData.end}:00` : formData.end)
        : null;

      // 2. ペイロード作成
      const payload = {
        title: formData.title,
        location: formData.location || "",
        description: formData.description || "",
        time_span_begin: startTimeISO,
        time_span_end: endTimeISO,
        
        // 既存のステータスと種別を維持 (これらがないと編集で未着手に戻ってしまうため)
        is_task: editTargetData ? editTargetData.is_task : true,
        status: editTargetData ? editTargetData.status : "未着手"
      };

      // 【重要】日付(date)フィールドの制御
      if (!startTimeISO) {
         // 時間指定がない(終日)タスクの場合のみ、dateを送信する
         payload.date = formData.date;
      } else {
         // 時間指定がある場合は、dateフィールド自体を送信しない(undefined)。
         // これにより、バックエンドはdateの更新をスキップし、
         // DBのNot Null制約違反(null送信時)と、バリデーションエラー(値送信時)の両方を回避する。
         payload.date = undefined; 
      }
      
      // undefinedのキーを削除（JSON化の際に消えるが念のため）
      Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);

      console.log("Sending payload:", payload);

      // 3. API送信
      if (editTargetData) {
        // 更新 (PUT)
        await api.put(`/groups/${groupId}/tasks/${editTargetData.id}`, payload);
      } else {
        // 新規作成 (POST)
        // 新規作成時はdate必須の可能性があるため、startTimeISOがあってもdateを入れる必要があるかもしれないが
        // 今回のバグは「編集(PUT)」なので、まずは編集を成功させるロジックとしています。
        // もし新規作成でエラーが出る場合は、POST時のみ payload.date = formData.date を強制します。
        if (!editTargetData && !payload.date) {
             payload.date = formData.date;
        }
        await api.post(`/groups/${groupId}/tasks/`, payload);
      }

      // 4. 成功時の処理
      setIsCreateModalOpen(false);
      setEditTargetData(null);
      fetchTasks();
      
    } catch (error) {
      console.error("Task operation failed:", error);
      
      // エラー情報の表示
      let errorMsg = "処理に失敗しました";
      const debugInfo = {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      };

      if (error.response?.data?.detail) {
        const { detail } = error.response.data;
        errorMsg = typeof detail === 'object' 
          ? `入力エラー:\n${JSON.stringify(detail, null, 2)}` 
          : detail;
      } else if (error.message === "Network Error") {
        errorMsg = "サーバーとの通信に失敗しました (Network Error)。\nバックエンドサーバーが停止しているか、クラッシュした可能性があります。\nサーバーを再起動してみてください。";
      } else {
        errorMsg = `エラーが発生しました:\n${JSON.stringify(debugInfo, null, 2)}`;
      }
      
      alert(errorMsg);
    }
  };

  const handleReactionUpdate = async (taskId, reactionType) => {
    try {
      await api.put(`/groups/${groupId}/tasks/${taskId}/reaction`, {
        reaction: reactionType,
        comment: "" 
      });
      fetchTasks();
      setIsDetailModalOpen(false);
    } catch (error) {
      alert("更新できませんでした");
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">グループカレンダー</h1>
          <p className="text-sm text-slate-500">
             {isAdmin ? "あなたは管理者です。予定の追加・編集が可能です。" : "予定の確認と参加表明ができます。"}
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={handleOpenCreateModal}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-bold hover:bg-primary-700 shadow-sm transition-colors"
          >
            ＋ 新規作成
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="h-[750px]">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek' }}
            locale="ja"
            firstDay={1}
            height="100%"
            events={events}
            
            eventClick={handleEventClick}
            eventDrop={handleEventDrop}
            eventResize={handleEventDrop}
            
            selectable={isAdmin}
            dateClick={handleDateSelect}
            
            editable={isAdmin}
          />
        </div>
      </div>

      <EventModal 
        isOpen={isDetailModalOpen} 
        onClose={() => setIsDetailModalOpen(false)} 
        event={selectedEvent}
        currentUser={currentUser}
        isAdmin={isAdmin} // 管理者権限を渡す
        onEdit={handleEditClick} // 編集ハンドラを渡す
        onReactionUpdate={handleReactionUpdate}
        readOnly={false}
      />

      <CreateEventModal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setEditTargetData(null); // 閉じる時に編集データをクリア
        }}
        onSubmit={handleFormSubmit}
        
        initialDate={initialDateStr}
        initialStartTime={initialStartTimeStr}
        initialData={editTargetData} // 編集データを渡す

        // keyを変えて再マウント（フォームリセット）
        key={isCreateModalOpen ? (editTargetData ? `edit-${editTargetData.id}` : 'create') : 'closed'}
      />
    </div>
  );
};

export default GroupCalendarPage;