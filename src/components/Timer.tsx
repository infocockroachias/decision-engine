"use client";

import { useEffect } from "react";

interface TimerProps {
  secondsRemaining: number;
  isRunning: boolean;
  onTimeUp: () => void;
  onTick?: (remaining: number) => void;
}

export default function Timer({ secondsRemaining, isRunning, onTimeUp, onTick }: TimerProps) {
  useEffect(() => {
    if (!isRunning || secondsRemaining <= 0) return;

    const interval = setInterval(() => {
      if (secondsRemaining <= 1) {
        clearInterval(interval);
        onTimeUp();
      }
      onTick?.(secondsRemaining - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, secondsRemaining, onTimeUp, onTick]);

  const minutes = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  const display = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

  const isWarning = secondsRemaining < 300; // Less than 5 minutes
  const isCritical = secondsRemaining < 60; // Less than 1 minute

  return (
    <div
      className={`flex items-center gap-2 rounded-lg px-4 py-2 font-mono text-lg font-bold transition-all
        ${isCritical ? "bg-red-100 text-red-700 timer-warning" : isWarning ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-700"}`}
      role="timer"
      aria-label={`Time remaining: ${display}`}
      aria-live={isWarning ? "assertive" : "polite"}
    >
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{display}</span>
      {isCritical && <span className="text-xs font-normal">Hurry!</span>}
    </div>
  );
}