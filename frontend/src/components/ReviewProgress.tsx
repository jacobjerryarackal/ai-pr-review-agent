"use client";

import { useState, useEffect } from "react";

interface ProgressEvent {
  status: string;
  message: string;
  percent: number;
}

export default function ReviewProgress({ reviewId }: { reviewId: string }) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `http://localhost:8000/api/reviews/${reviewId}/stream`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);

      if (data.status === "completed" || data.status === "failed") {
        setIsComplete(true);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      setIsComplete(true);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [reviewId]);

  const currentEvent = events[events.length - 1];
  const progress = currentEvent?.percent ?? 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold mb-4">Review Progress</h3>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Status */}
      <p className="text-gray-700">
        {currentEvent?.message ?? "Starting..."}
      </p>

      {/* Event Log */}
      <div className="mt-4 space-y-1">
        {events.map((event, i) => (
          <div key={i} className="text-sm text-gray-500">
            [{event.status}] {event.message}
          </div>
        ))}
      </div>

      {isComplete && (
        <p className="mt-4 text-green-600 font-medium">Review complete!</p>
      )}
    </div>
  );
}