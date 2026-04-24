import { useState, useEffect } from 'react';
import { getSamples, loadSample } from '../api';
import type { SampleDataset, SampleLoadResponse } from '../types';

interface SampleDatasetsProps {
  onSampleLoaded: (data: SampleLoadResponse) => void;
}

export default function SampleDatasets({ onSampleLoaded }: SampleDatasetsProps) {
  const [samples, setSamples] = useState<SampleDataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSamples = async () => {
      try {
        const data = await getSamples();
        setSamples(data);
      } catch (err) {
        setError('Failed to load sample datasets');
      }
    };
    fetchSamples();
  }, []);

  const handleLoadSample = async (name: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await loadSample(name);
      onSampleLoaded(data);
    } catch (err) {
      setError(`Failed to load sample: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8">
      <div className="flex items-center gap-4 mb-4">
        <div className="flex-1 h-px bg-outline-variant"></div>
        <span className="text-body-sm text-on-surface-variant">Or try a sample dataset</span>
        <div className="flex-1 h-px bg-outline-variant"></div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-error-container rounded-lg">
          <p className="text-body-md text-on-error-container">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {samples.map((sample) => (
          <div
            key={sample.name}
            className="bg-surface-container-low rounded-lg p-6 hover:bg-surface-container transition-colors"
          >
            <h3 className="text-title-md font-medium text-on-surface mb-2">
              {sample.display_name}
            </h3>
            <p className="text-body-sm text-on-surface-variant mb-3">
              {sample.description}
            </p>
            <div className="flex items-center gap-4 text-label-sm text-on-surface-variant mb-4">
              <span>{sample.row_count.toLocaleString()} rows</span>
              <span>•</span>
              <span>{sample.column_count} columns</span>
            </div>
            <button
              onClick={() => handleLoadSample(sample.name)}
              disabled={loading}
              className="w-full px-4 py-2 bg-primary text-on-primary rounded-lg hover:shadow-md transition-shadow disabled:opacity-50 disabled:cursor-not-allowed text-body-md font-medium"
            >
              {loading ? 'Loading...' : 'Load Dataset'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
