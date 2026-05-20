import React from 'react';

interface ProgressBarProps {
  value: number; // 0–100
  label?: string;
  className?: string;
}

export default function ProgressBar({ value, label, className = '' }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div className={['w-full', className].join(' ')}>
      {(label !== undefined) && (
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{label}</span>
          <span>{clamped.toFixed(0)}%</span>
        </div>
      )}
      {label === undefined && (
        <div className="flex justify-end text-xs text-gray-500 mb-1">
          <span>{clamped.toFixed(0)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className="bg-abs-blue-light h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
