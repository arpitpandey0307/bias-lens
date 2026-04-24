import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { GroupStatistics } from '../types';

interface ApprovalRateChartProps {
  groupStatistics: Record<string, GroupStatistics>;
}

export default function ApprovalRateChart({ groupStatistics }: ApprovalRateChartProps) {
  const data = Object.entries(groupStatistics).map(([group, stats]) => ({
    group,
    approvalRate: stats.approval_rate * 100,
    count: stats.total_count,
  }));

  // Sort by approval rate descending
  data.sort((a, b) => b.approvalRate - a.approvalRate);

  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
      <h3 className="text-headline-sm font-medium text-on-surface mb-4">
        Approval Rates by Group
      </h3>
      <p className="text-body-md text-on-surface-variant mb-6">
        Percentage of positive outcomes for each demographic group
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e1e6f0" opacity={0.3} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
            stroke="#44474f"
            style={{ fontSize: '0.875rem' }}
          />
          <YAxis
            type="category"
            dataKey="group"
            stroke="#44474f"
            style={{ fontSize: '0.875rem' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e1e6f0',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
            }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, 'Approval Rate']}
          />
          <Bar dataKey="approvalRate" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill="url(#primaryGradient)"
              />
            ))}
          </Bar>
          <defs>
            <linearGradient id="primaryGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#003d9b" />
              <stop offset="100%" stopColor="#0052cc" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4">
        {data.map((item) => (
          <div key={item.group} className="text-label-sm text-on-surface-variant">
            <span className="font-medium text-on-surface">{item.group}:</span> {item.count} samples
          </div>
        ))}
      </div>
    </div>
  );
}
