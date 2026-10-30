// Just a standard component, nothing fancy here.

// Represents a user in the system
export interface User {
  id: number;
  email: string;
  full_name: string;
}

// Data needed to log in
export interface LoginRequest {
  username: string;
  password: string;
}

// Data needed to sign up
export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

// The response from the server after a successful login
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// A single blood test measurement (e.g. Hemoglobin)
export interface TestResult {
  id: number;
  report_id: number;
  test_name: string;
  value: number;
  unit: string;
  reference_low: number | null; // The lowest normal value
  reference_high: number | null; // The highest normal value
  status: 'NORMAL' | 'LOW' | 'HIGH' | 'UNKNOWN'; // AI determined status
  ocr_confidence: number | null; // How confident the text reader was
  ai_explanation: string | null; // Simple explanation of the test
  category: string | null;
}

// A complete lab report document containing multiple test results
export interface Report {
  id: number;
  user_id: number;
  filename: string;
  upload_date: string;
  report_date: string | null;
  patient_name: string | null;
  ai_summary: string | null; // Overall summary of all results
  total_tests: number;
  normal_count: number;
  low_count: number;
  high_count: number;
  is_demo: boolean;
  test_results: TestResult[]; // List of individual tests in this report
}

// A simplified version of a Report used for lists/tables
export interface ReportListItem {
  id: number;
  filename: string;
  upload_date: string;
  report_date: string | null;
  patient_name: string | null;
  total_tests: number;
  normal_count: number;
  low_count: number;
  high_count: number;
  is_demo: boolean;
}

// Compares a single test across two different reports
export interface ComparisonResult {
  test_name: string;
  report1_value: number;
  report1_unit: string;
  report1_status: string;
  report2_value: number;
  report2_unit: string;
  report2_status: string;
  change: number; // Difference between the two values
}

// Holds the full comparison data for two reports
export interface ReportComparison {
  report1: ReportListItem;
  report2: ReportListItem;
  comparisons: ComparisonResult[];
}

// The different stages a file goes through when uploaded
export type ProcessingStage = 
  | 'uploading'
  | 'reading'
  | 'extracting'
  | 'comparing'
  | 'explaining'
  | 'complete'
  | 'error';
