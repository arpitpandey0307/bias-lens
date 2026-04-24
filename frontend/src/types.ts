// API Response Types
export interface UploadResponse {
  session_id: string;
  filename: string;
  size_bytes: number;
  row_count: number;
  column_count: number;
  preview: Record<string, any>[];
  warnings: { type: string; message: string }[];
}

export interface ColumnInfo {
  name: string;
  detected_type: 'numeric' | 'categorical' | 'binary' | 'text';
  unique_values: number;
  missing_percentage: number;
  sample_values: any[];
}

export interface ProtectedAttributeSuggestion {
  column: string;
  confidence: 'high' | 'medium' | 'low';
  detected_groups: string[];
}

export interface OutcomeSuggestion {
  column: string;
  confidence: 'high' | 'medium' | 'low';
}

export interface SchemaSuggestions {
  protected_attributes: ProtectedAttributeSuggestion[];
  outcome_column: OutcomeSuggestion;
  feature_columns: string[];
}

export interface SchemaWarning {
  column: string;
  issue: 'high_missing' | 'too_many_categories' | 'low_variance';
  message: string;
}

export interface SchemaValidationResponse {
  columns: ColumnInfo[];
  suggestions: SchemaSuggestions;
  warnings: SchemaWarning[];
}


// Analysis Types
export interface MetricResult {
  value: number;
  threshold_status: 'pass' | 'warning' | 'fail';
  by_group: Record<string, number>;
}

export interface ConfusionMatrixData {
  true_positive: number;
  false_positive: number;
  true_negative: number;
  false_negative: number;
}

export interface GroupStatistics {
  total_count: number;
  positive_outcomes: number;
  approval_rate: number;
  confusion_matrix: ConfusionMatrixData;
}

export interface FairnessAnalysisResponse {
  analysis_id: string;
  protected_groups: string[];
  metrics: Record<string, MetricResult>;
  group_statistics: Record<string, GroupStatistics>;
  computation_time_ms: number;
}


// Export Types
export interface ExportRequest {
  analysis_id: string;
  format: 'pdf' | 'html';
  include_sections?: {
    executive_summary?: boolean;
    data_overview?: boolean;
    fairness_metrics?: boolean;
    visualizations?: boolean;
    recommendations?: boolean;
  };
}

export interface ExportResponse {
  report_id: string;
  download_url: string;
  filename: string;
  size_bytes: number;
  generated_at: string;
  expires_at: string;
}

// Sample Dataset Types
export interface SampleDataset {
  name: string;
  display_name: string;
  description: string;
  prediction_task: string;
  protected_attributes: string[];
  outcome_column: string;
  row_count: number;
  column_count: number;
}

export interface SampleLoadResponse extends UploadResponse {
  suggested_protected_attr: string;
  suggested_outcome: string;
}
