import { useState } from 'react';
import type { MetricResult } from '../types';

interface MetricCardProps {
  title: string;
  metric: MetricResult;
  description: string;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pass':
      return 'bg-background-success text-text-success border-text-success';
    case 'warning':
      return 'bg-tertiary-container text-on-tertiary-fixed-variant border-tertiary';
    case 'fail':
      return 'bg-error-container text-on-error-container border-error';
    default:
      return 'bg-surface-variant text-on-surface-variant';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'pass':
      return '✓';
    case 'warning':
      return '⚠';
    case 'fail':
      return '✕';
    default:
      return '?';
  }
};

export default function MetricCard({ title, metric, description }: MetricCardProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative bg-surface-container-lowest rounded-lg shadow-ambient p-6 hover:shadow-lg transition-shadow">
      {/* Status Indicator */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-body-md font-medium text-on-surface mb-1">{title}</h3>
          <div className="text-display-md font-medium text-on-surface">
            {metric.value.toFixed(3)}
          </div>
        </div>
        <div
          className={`
            w-12 h-12 rounded-full flex items-center justify-center text-xl font-medium
            border-2 ${getStatusColor(metric.threshold_status)}
          `}
        >
          {getStatusIcon(metric.threshold_status)}
        </div>
      </div>

      {/* Status Label */}
      <div className="mb-3">
        <span
          className={`
            inline-block px-3 py-1 rounded-full text-label-sm font-medium uppercase tracking-wider
            ${getStatusColor(metric.threshold_status)}
          `}
        >
          {metric.threshold_status}
        </span>
      </div>

      {/* Info Button */}
      <button
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="text-label-sm text-primary hover:underline"
      >
        What does this mean?
      </button>

      {/* Tooltip */}
      {showTooltip && (
        <div
          className="absolute z-10 bottom-full left-0 right-0 mb-2 p-4 rounded-lg
                     bg-surface-container-highest/70 backdrop-blur-[24px] shadow-ambient
                     text-body-md text-on-surface"
          style={{ backdropFilter: 'blur(24px)' }}
        >
          {description}
        </div>
      )}
    </div>
  );
}
