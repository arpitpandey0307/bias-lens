import { useEffect, useState } from 'react';
import { validateSchema } from '../api';
import type { SchemaValidationResponse } from '../types';

interface SchemaValidatorProps {
  sessionId: string;
  onValidationComplete: (data: SchemaValidationResponse, protectedAttr: string, outcome: string) => void;
}

export default function SchemaValidator({ sessionId, onValidationComplete }: SchemaValidatorProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<SchemaValidationResponse | null>(null);
  const [selectedProtectedAttr, setSelectedProtectedAttr] = useState<string>('');
  const [selectedOutcome, setSelectedOutcome] = useState<string>('');

  useEffect(() => {
    const loadSchema = async () => {
      try {
        const response = await validateSchema(sessionId);
        setSchema(response);
        
        // Set defaults from suggestions
        if (response.suggestions.protected_attributes.length > 0) {
          setSelectedProtectedAttr(response.suggestions.protected_attributes[0].column);
        }
        setSelectedOutcome(response.suggestions.outcome_column.column);
        
        setLoading(false);
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to validate schema');
        setLoading(false);
      }
    };

    loadSchema();
  }, [sessionId]);

  const handleAnalyze = () => {
    if (schema && selectedProtectedAttr && selectedOutcome) {
      onValidationComplete(schema, selectedProtectedAttr, selectedOutcome);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-body-md text-on-surface-variant">Analyzing schema...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-error-container rounded-lg">
        <p className="text-body-md text-on-error-container">{error}</p>
      </div>
    );
  }

  if (!schema) return null;

  const isValid = selectedProtectedAttr && selectedOutcome;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-headline-sm font-medium text-on-surface mb-4">
          Schema Configuration
        </h3>
        <p className="text-body-md text-on-surface-variant">
          Review detected columns and confirm your selections
        </p>
      </div>

      {/* Warnings */}
      {schema.warnings.length > 0 && (
        <div className="space-y-2">
          {schema.warnings.map((warning, idx) => (
            <div key={idx} className="p-3 bg-tertiary-container rounded-lg">
              <p className="text-body-md text-on-tertiary-fixed-variant">
                ⚠️ {warning.message}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Protected Attribute Selection */}
      <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
        <label className="block text-body-md font-medium text-on-surface mb-2">
          Protected Attribute
        </label>
        <p className="text-label-sm text-on-surface-variant mb-3">
          Select the demographic feature to analyze for bias (e.g., gender, race, age group). Must have 2-10 groups.
        </p>
        <select
          value={selectedProtectedAttr}
          onChange={(e) => setSelectedProtectedAttr(e.target.value)}
          className="w-full px-4 py-2 border border-outline-variant rounded-md bg-surface focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Select a column...</option>
          {schema.suggestions.protected_attributes
            .filter(attr => attr.detected_groups.length >= 2 && attr.detected_groups.length <= 10)
            .map((attr) => (
              <option key={attr.column} value={attr.column}>
                {attr.column} ({attr.confidence} confidence) - {attr.detected_groups.length} groups
              </option>
            ))}
        </select>
        
        {selectedProtectedAttr && (
          <div className="mt-3 p-3 bg-surface-container-low rounded">
            <p className="text-label-sm text-on-surface-variant mb-1">Detected groups:</p>
            <div className="flex flex-wrap gap-2">
              {schema.suggestions.protected_attributes
                .find(a => a.column === selectedProtectedAttr)
                ?.detected_groups.map((group) => (
                  <span
                    key={group}
                    className="px-2 py-1 bg-background-info text-text-info text-label-sm rounded"
                  >
                    {group}
                  </span>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Outcome Column Selection */}
      <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
        <label className="block text-body-md font-medium text-on-surface mb-2">
          Outcome Column
        </label>
        <p className="text-label-sm text-on-surface-variant mb-3">
          Select the decision or result column (e.g., hired, approved, admitted)
        </p>
        <select
          value={selectedOutcome}
          onChange={(e) => setSelectedOutcome(e.target.value)}
          className="w-full px-4 py-2 border border-outline-variant rounded-md bg-surface focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Select a column...</option>
          {schema.columns
            .filter(col => col.detected_type === 'binary' || col.unique_values === 2)
            .map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} ({col.unique_values} unique values)
              </option>
            ))}
        </select>
      </div>

      {/* Column Summary */}
      <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
        <h4 className="text-body-md font-medium text-on-surface mb-3">
          All Columns ({schema.columns.length})
        </h4>
        <div className="space-y-2">
          {schema.columns.map((col) => (
            <div
              key={col.name}
              className="flex justify-between items-center p-3 bg-surface-container-low rounded"
            >
              <div>
                <span className="text-body-md text-on-surface font-medium">{col.name}</span>
                <span className="ml-2 text-label-sm text-on-surface-variant">
                  {col.detected_type}
                </span>
              </div>
              <div className="text-label-sm text-on-surface-variant">
                {col.unique_values} unique · {col.missing_percentage.toFixed(1)}% missing
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={handleAnalyze}
        disabled={!isValid}
        className={`
          w-full py-3 px-6 rounded-lg font-medium text-on-primary
          transition-all duration-200
          ${isValid
            ? 'bg-gradient-to-br from-primary to-primary-container hover:shadow-lg'
            : 'bg-surface-variant text-on-surface-variant cursor-not-allowed'
          }
        `}
      >
        Analyze Fairness
      </button>
    </div>
  );
}
