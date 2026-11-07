import React from 'react';

interface SparklineProps {
  color?: 'blue' | 'green' | 'purple' | 'amber' | 'cyan';
  width?: number;
  height?: number;
  className?: string;
}

export const Sparkline: React.FC<SparklineProps> = ({
  color = 'blue',
  width = 120,
  height = 36,
  className = '',
}) => {
  const gradientId = `spark-grad-${color}-${Math.random().toString(36).substr(2, 9)}`;

  const colorMap = {
    blue: {
      stroke: '#3b82f6',
      stopColor: '#3b82f6',
      d: 'M0,28 C20,32 35,16 55,22 C75,28 90,8 110,14 C115,16 118,10 120,8',
    },
    green: {
      stroke: '#10b981',
      stopColor: '#10b981',
      d: 'M0,30 C25,24 45,34 65,18 C85,2 100,20 120,10',
    },
    purple: {
      stroke: '#8b5cf6',
      stopColor: '#8b5cf6',
      d: 'M0,26 C20,28 40,12 60,20 C80,28 100,10 120,16',
    },
    amber: {
      stroke: '#f59e0b',
      stopColor: '#f59e0b',
      d: 'M0,24 C20,30 45,18 70,24 C95,30 105,12 120,14',
    },
    cyan: {
      stroke: '#06b6d4',
      stopColor: '#06b6d4',
      d: 'M0,26 C25,32 45,14 70,22 C95,30 105,12 120,8',
    },
  };

  const current = colorMap[color];

  return (
    <svg
      viewBox="0 0 120 36"
      width={width}
      height={height}
      className={`overflow-visible ${className}`}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={current.stopColor} stopOpacity="0.28" />
          <stop offset="100%" stopColor={current.stopColor} stopOpacity="0.0" />
        </linearGradient>
      </defs>
      <path
        d={`${current.d} L120,36 L0,36 Z`}
        fill={`url(#${gradientId})`}
      />
      <path
        d={current.d}
        stroke={current.stroke}
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

