import { useState } from 'react'
import UploadComponent from './components/UploadComponent'
import PreviewTable from './components/PreviewTable'
import SchemaValidator from './components/SchemaValidator'
import Dashboard from './components/Dashboard'
import SampleDatasets from './components/SampleDatasets'
import type { UploadResponse, SchemaValidationResponse, SampleLoadResponse } from './types'

type AppState = 'upload' | 'schema' | 'analysis';

function App() {
  const [state, setState] = useState<AppState>('upload');
  const [uploadData, setUploadData] = useState<UploadResponse | null>(null);
  const [, setSchemaData] = useState<SchemaValidationResponse | null>(null);
  const [selectedProtectedAttr, setSelectedProtectedAttr] = useState<string>('');
  const [selectedOutcome, setSelectedOutcome] = useState<string>('');

  const handleUploadSuccess = (data: UploadResponse) => {
    setUploadData(data);
    setState('schema');
  };

  const handleSampleLoaded = (data: SampleLoadResponse) => {
    setUploadData(data);
    setSelectedProtectedAttr(data.suggested_protected_attr);
    setSelectedOutcome(data.suggested_outcome);
    setState('schema');
  };

  const handleValidationComplete = (
    data: SchemaValidationResponse,
    protectedAttr: string,
    outcome: string
  ) => {
    setSchemaData(data);
    setSelectedProtectedAttr(protectedAttr);
    setSelectedOutcome(outcome);
    setState('analysis');
  };

  const handleReset = () => {
    setUploadData(null);
    setSchemaData(null);
    setSelectedProtectedAttr('');
    setSelectedOutcome('');
    setState('upload');
  };

  return (
    <div className="min-h-screen bg-surface">
      <header className="bg-surface-container-lowest shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-headline-sm font-medium text-on-surface">
                BiasLens — Fairness Auditor
              </h1>
              <p className="text-body-md text-on-surface-variant mt-1">
                Plug-and-play fairness auditor for non-technical users
              </p>
            </div>
            {state !== 'upload' && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-body-md text-primary hover:bg-surface-container-high rounded-lg transition-colors"
              >
                New Analysis
              </button>
            )}
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {state === 'upload' && (
          <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-8">
            <h2 className="text-xl font-medium text-on-surface mb-6">
              Upload Your Data
            </h2>
            <UploadComponent onUploadSuccess={handleUploadSuccess} />
            <SampleDatasets onSampleLoaded={handleSampleLoaded} />
          </div>
        )}

        {state === 'schema' && uploadData && (
          <div className="space-y-6">
            <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-8">
              <PreviewTable
                data={uploadData.preview}
                rowCount={uploadData.row_count}
                columnCount={uploadData.column_count}
              />
            </div>
            
            <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-8">
              <SchemaValidator
                sessionId={uploadData.session_id}
                onValidationComplete={handleValidationComplete}
              />
            </div>
          </div>
        )}

        {state === 'analysis' && uploadData && (
          <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-8">
            <Dashboard
              sessionId={uploadData.session_id}
              protectedAttribute={selectedProtectedAttr}
              outcomeColumn={selectedOutcome}
            />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
