import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadCSV } from '../api';
import type { UploadResponse } from '../types';

interface UploadComponentProps {
  onUploadSuccess: (data: UploadResponse) => void;
}

export default function UploadComponent({ onUploadSuccess }: UploadComponentProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Client-side validation
    if (file.size > 50 * 1024 * 1024) {
      setError('File too large. Maximum size is 50MB.');
      return;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Invalid file format. Please upload a CSV file.');
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const response = await uploadCSV(file);
      onUploadSuccess(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Upload failed. Please try again.';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive 
            ? 'border-primary bg-surface-container-highest scale-105' 
            : 'border-outline-variant bg-surface-container-low hover:bg-surface-container-high'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          <svg
            className="w-16 h-16 text-on-surface-variant"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          {uploading ? (
            <div className="text-body-md text-on-surface-variant">
              Uploading...
            </div>
          ) : (
            <>
              <div className="text-body-md text-on-surface">
                {isDragActive ? (
                  'Drop your CSV file here'
                ) : (
                  <>
                    <span className="font-medium text-primary">Click to upload</span>
                    {' or drag and drop'}
                  </>
                )}
              </div>
              <div className="text-label-sm text-on-surface-variant">
                CSV files up to 50MB
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-error-container rounded-lg">
          <p className="text-body-md text-on-error-container">{error}</p>
        </div>
      )}
    </div>
  );
}
