import React from 'react';

interface BadgeProps {
  status: string;
  className?: string;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  draft:           { label: 'Draft',           className: 'bg-gray-100 text-gray-600' },
  clarifying:      { label: 'Clarifying',      className: 'bg-sky-100 text-sky-700' },
  scenarios_ready: { label: 'Scenarios Ready', className: 'bg-sky-100 text-sky-700' },
  configured:      { label: 'Configured',      className: 'bg-sky-100 text-sky-700' },
  locked:          { label: 'Locked',          className: 'bg-yellow-100 text-yellow-700' },
  running:         { label: 'Running',         className: 'bg-blue-100 text-blue-700 animate-pulse' },
  results_ready:   { label: 'Results Ready',   className: 'bg-green-100 text-green-700' },
  rollout_ready:   { label: 'Rollout Ready',   className: 'bg-abs-blue-dark text-white' },
  complete:        { label: 'Complete',        className: 'bg-abs-blue-dark text-white' },
};

export default function Badge({ status, className = '' }: BadgeProps) {
  const cfg = statusConfig[status] ?? { label: status, className: 'bg-gray-100 text-gray-600' };
  return (
    <span
      className={[
        'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold',
        cfg.className,
        className,
      ].join(' ')}
    >
      {cfg.label}
    </span>
  );
}
