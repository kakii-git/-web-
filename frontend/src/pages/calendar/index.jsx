// frontend/src/pages/calendar/index.jsx
import React, { useState, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import api from '../../lib/api'; // src/lib/api.js

import EventModal from './EventModal';

const CalendarPage = () => {
  const [events, setEvents] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  const calendarRef = useRef(null);

  // カレンダーの表示月が変わるたびにバックエンドからデータを取得
  const handleDatesSet = async (dateInfo) => {
    // 表示中の中心となる日付から「年」「月」を計算
    const centerDate = dateInfo.view.currentStart;
    const year = centerDate.getFullYear();
    const month = centerDate.getMonth() + 1;

    try {
      // 既存API: /my-tasks (自分専用、グループ横断)
      const response = await api.get('/my-tasks', {
        params: { year, month }
      });

      // APIレスポンス (GlobalCalendarTaskResponse) を FullCalendar 用に変換
      const mappedEvents = response.data.map(task => ({
        id: task.task_id,
        title: task.title,
        start: task.time_span_begin || task.date, 
        end: task.time_span_end,
        color: '#6366f1', // 個人の予定カラー
        extendedProps: {
          groupName: task.group_name, // APIから返ってくるグループ名
          location: task.location,
          description: task.description || '詳細なし',
        }
      }));
      
      setEvents(mappedEvents);
    } catch (error) {
      console.error("Failed to fetch my tasks:", error);
    }
  };

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
    setIsModalOpen(true);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 relative">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-slate-800">マイカレンダー</h2>
        <p className="text-sm text-slate-500">参加中の全グループのタスクが表示されます（閲覧専用）</p>
      </div>

      <div className="h-[750px]">
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
          }}
          locale="ja"
          firstDay={1}
          height="100%"
          
          events={events}
          datesSet={handleDatesSet} // 表示期間変更時にデータ取得
          eventClick={handleEventClick}
          
          // ▼ 要件: 個人画面では移動・追加不可
          editable={false}
          selectable={false}
          dayMaxEvents={true}
        />
      </div>

      <EventModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        event={selectedEvent}
        // 個人カレンダーからはリアクション操作をさせない（グループ画面へ誘導）
        readOnly={true}
      />
    </div>
  );
};

export default CalendarPage;