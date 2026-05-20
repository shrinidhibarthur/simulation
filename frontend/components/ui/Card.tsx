import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div className={['bg-white border border-gray-200 rounded-lg p-6', className].join(' ')}>
      {children}
    </div>
  );
}
