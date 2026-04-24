import axios from 'axios';
import type { UploadResponse, SchemaValidationResponse, FairnessAnalysisResponse, ExportResponse, SampleDataset, SampleLoadResponse } from './types';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadCSV = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const validateSchema = async (sessionId: string): Promise<SchemaValidationResponse> => {
  const response = await api.post<SchemaValidationResponse>('/api/validate-schema', {
    session_id: sessionId,
  });
  
  return response.data;
};

export default api;


export const analyzeFairness = async (
  sessionId: string,
  protectedAttribute: string,
  outcomeColumn: string,
  featureColumns: string[] = []
): Promise<FairnessAnalysisResponse> => {
  const response = await api.post<FairnessAnalysisResponse>('/api/analyze', {
    session_id: sessionId,
    protected_attribute: protectedAttribute,
    outcome_column: outcomeColumn,
    feature_columns: featureColumns,
  });
  
  return response.data;
};


export const exportReport = async (
  analysisId: string,
  format: 'pdf' | 'html' = 'pdf'
): Promise<ExportResponse> => {
  const response = await api.post<ExportResponse>('/api/export', {
    analysis_id: analysisId,
    format: format,
    include_sections: {
      executive_summary: true,
      data_overview: true,
      fairness_metrics: true,
      visualizations: true,
      recommendations: true,
    },
  });
  
  return response.data;
};

export const downloadReport = (reportId: string) => {
  const downloadUrl = `${API_BASE_URL}/api/download/${reportId}`;
  window.open(downloadUrl, '_blank');
};

// Sample Datasets API
export const getSamples = async (): Promise<SampleDataset[]> => {
  const response = await api.get<SampleDataset[]>('/api/samples/');
  return response.data;
};

export const loadSample = async (name: string): Promise<SampleLoadResponse> => {
  const response = await api.post<SampleLoadResponse>(`/api/samples/${name}/load`);
  return response.data;
};
