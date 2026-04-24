import { useEffect, useState } from 'react';
import { analyzeFairness } from '../api';
import type { FairnessAnalysisResponse } from '../types';
import MetricCard from './MetricCard';
import ApprovalRateChart from './ApprovalRateChart';
import ConfusionMatrixHeatmap from './ConfusionMatrixHeatmap';
import ReportExporter from './ReportExporter';

interface DashboardProps {
  sessionId: string;
  protectedAttribute: string;
  outcomeColumn: string;
}

const METRIC_DESCRIPTIONS = {
  statistical_parity_difference: 'Measures the difference in approval rates between groups. Values close to 0 indicate fairness. Negative values mean the reference group has lower approval rates.',
  disparate_impact: 'Ratio of approval rates between groups. Values close to 1.0 indicate fairness. Values below 0.8 or above 1.25 suggest potential bias.',
  equal_opportunity_difference: 'Measures the difference in true positive rates (correctly identifying qualified candidates) between groups. Values close to 0 indicate equal opportunity.',
  predictive_parity_difference: 'Measures the difference in positive predictive values (accuracy of positive predictions) between groups. Values close to 0 indicate fairness.',
};

const METRIC_TITLES = {
  statistical_parity_difference: 'Statistical Parity',
  disparate_impact: 'Disparate Impact',
  equal_opportunity_difference: 'Equal Opportunity',
  predictive_parity_difference: 'Predictive Parity',
};

export default function Dashboard({ sessionId, protectedAttribute, outcomeColumn }: DashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<FairnessAnalysisResponse | null>(null);

  useEffect(() => {
    const runAnalysis = async () => {
      try {
        setLoading(true);
        const result = await analyzeFairness(sessionId, protectedAttribute, outcomeColumn);
        setAnalysis(result);
        setError(null);
      } catch (err: any) {
        const detail = err.response?.data?.detail;
        const message = typeof detail === 'object' ? detail?.message : (typeof detail === 'string' ? detail : err.response?.data?.message);
        setError(message || 'Analysis failed. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    runAnalysis();
  }, [sessionId, protectedAttribute, outcomeColumn]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-body-md text-on-surface-variant">Computing fairness metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-error-container rounded-lg">
        <h3 className="text-body-md font-medium text-on-error-container mb-2">Analysis Error</h3>
        <p className="text-body-md text-on-error-container">{error}</p>
      </div>
    );
  }

  if (!analysis) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-headline-sm font-medium text-on-surface mb-2">
          Fairness Analysis Results
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Analyzing {analysis.protected_groups.length} groups · Computed in {analysis.computation_time_ms}ms
        </p>
      </div>

      {/* Metric Scorecards */}
      <div>
        <h3 className="text-body-md font-medium text-on-surface mb-4 uppercase tracking-wider text-on-surface-variant">
          Fairness Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(analysis.metrics).map(([key, metric]) => (
            <MetricCard
              key={key}
              title={METRIC_TITLES[key as keyof typeof METRIC_TITLES] || key}
              metric={metric}
              description={METRIC_DESCRIPTIONS[key as keyof typeof METRIC_DESCRIPTIONS] || ''}
            />
          ))}
        </div>
      </div>

      {/* Approval Rate Chart */}
      <ApprovalRateChart groupStatistics={analysis.group_statistics} />

      {/* Confusion Matrices */}
      <ConfusionMatrixHeatmap groupStatistics={analysis.group_statistics} />

      {/* Group Comparison Table */}
      <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
        <h3 className="text-headline-sm font-medium text-on-surface mb-4">
          Group Comparison
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low">
                <th className="px-4 py-3 text-left text-label-sm uppercase tracking-wider text-on-surface-variant font-medium">
                  Group
                </th>
                <th className="px-4 py-3 text-right text-label-sm uppercase tracking-wider text-on-surface-variant font-medium">
                  Total
                </th>
                <th className="px-4 py-3 text-right text-label-sm uppercase tracking-wider text-on-surface-variant font-medium">
                  Approved
                </th>
                <th className="px-4 py-3 text-right text-label-sm uppercase tracking-wider text-on-surface-variant font-medium">
                  Approval Rate
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(analysis.group_statistics).map(([group, stats], idx) => (
                <tr
                  key={group}
                  className={idx % 2 === 0 ? 'bg-surface' : 'bg-surface-container-low'}
                >
                  <td className="px-4 py-3 text-body-md text-on-surface font-medium">{group}</td>
                  <td className="px-4 py-3 text-body-md text-on-surface text-right">
                    {stats.total_count.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-body-md text-on-surface text-right">
                    {stats.positive_outcomes.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-body-md text-on-surface text-right font-medium">
                    {(stats.approval_rate * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Report Exporter */}
      <ReportExporter analysisId={analysis.analysis_id} />
    </div>
  );
}
