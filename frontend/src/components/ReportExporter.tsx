import { useState } from 'react';
import { exportReport, downloadReport } from '../api';

interface ReportExporterProps {
  analysisId: string;
}

export default function ReportExporter({ analysisId }: ReportExporterProps) {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleExport = async (format: 'pdf' | 'html') => {
    setGenerating(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await exportReport(analysisId, format);
      
      // Automatically trigger download
      downloadReport(response.report_id);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate report. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
      <h3 className="text-headline-sm font-medium text-on-surface mb-2">
        Export Report
      </h3>
      <p className="text-body-md text-on-surface-variant mb-6">
        Generate a compliance-ready report with all fairness metrics, visualizations, and recommendations
      </p>

      <div className="flex gap-4">
        <button
          onClick={() => handleExport('pdf')}
          disabled={generating}
          className={`
            flex-1 py-3 px-6 rounded-lg font-medium text-on-primary
            transition-all duration-200
            ${generating
              ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed'
              : 'bg-gradient-to-br from-primary to-primary-container hover:shadow-lg'
            }
          `}
        >
          {generating ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Export PDF Report
            </span>
          )}
        </button>

        {/* HTML export disabled for now */}
        <button
          disabled
          className="flex-1 py-3 px-6 rounded-lg font-medium bg-surface-variant text-on-surface-variant cursor-not-allowed"
        >
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
              />
            </svg>
            HTML (Coming Soon)
          </span>
        </button>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mt-4 p-4 bg-background-success rounded-lg">
          <p className="text-body-md text-text-success flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            Report generated successfully! Download should start automatically.
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-error-container rounded-lg">
          <p className="text-body-md text-on-error-container">{error}</p>
        </div>
      )}

      {/* Report Details */}
      <div className="mt-6 p-4 bg-surface-container-low rounded-lg">
        <h4 className="text-body-md font-medium text-on-surface mb-3">Report Includes:</h4>
        <ul className="space-y-2 text-body-md text-on-surface-variant">
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>Executive summary with fairness assessment</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>All fairness metrics with traffic-light indicators</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>Group statistics and approval rates</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>Confusion matrices for each demographic group</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>Actionable recommendations</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-text-success mt-0.5">✓</span>
            <span>Compliance-ready cover sheet with timestamp</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
