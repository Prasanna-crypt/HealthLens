import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileDropZone } from '../components/upload/FileDropZone';
import { FilePreview } from '../components/upload/FilePreview';
import { UploadProgress } from '../components/upload/UploadProgress';
import { reportsAPI } from '../lib/api';
import type { ProcessingStage, TestResult } from '../lib/types';
import { 
  Check, 
  FileText, 
  Activity, 
  ShieldCheck, 
  Plus, 
  Trash2, 
  ArrowRight, 
  RefreshCw,
  Sparkles,
  ArrowRightLeft,
  AlertTriangle
} from 'lucide-react';

export const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stage, setStage] = useState<ProcessingStage>('uploading');
  const [uploadPercent, setUploadPercent] = useState(0);
  const [error, setError] = useState<string | undefined>();
  
  const [extractedData, setExtractedData] = useState<TestResult[] | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);
  
  const navigate = useNavigate();

  const handleInitialAnalyze = async () => {
    if (!file) return;
    setIsProcessing(true);
    setError(undefined);
    setStage('uploading');

    try {
      const res = await reportsAPI.extract(file);
      const results = res.data.extracted_results || [];
      if (results.length === 0) {
        setError("No lab test values could be detected in this document. Please verify the document contains clear printed test results (e.g., Hemoglobin, Glucose, Cholesterol).");
        setStage('error');
        setIsProcessing(false);
        return;
      }
      const data = results.map((r: any, idx: number) => ({
        ...r, id: idx,
      }));
      setExtractedData(data);
      setIsProcessing(false);
      setStage('complete');
    } catch (err: any) {
      setError(err.response?.data?.detail || err?.message || 'An error occurred during extraction.');
      setStage('error');
      setIsProcessing(false);
    }
  };

  const handleDataChange = (id: number, field: keyof TestResult, value: any) => {
    if (!extractedData) return;
    setExtractedData(extractedData.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const handleRemoveRow = (id: number) => {
    if (!extractedData) return;
    setExtractedData(extractedData.filter(item => item.id !== id));
  };

  const handleAddRow = () => {
    if (!extractedData) return;
    const newId = extractedData.length > 0 ? Math.max(...extractedData.map(d => d.id || 0)) + 1 : 1;
    const newRow: TestResult = {
      id: newId,
      report_id: 0,
      test_name: 'New Test',
      value: 0,
      unit: '',
      reference_low: 0,
      reference_high: 0,
      status: 'NORMAL',
      ocr_confidence: 1.0,
      ai_explanation: '',
      category: 'General',
    };
    setExtractedData([...extractedData, newRow]);
  };

  const handleConfirmAndAnalyze = async () => {
    if (!file || !extractedData) return;
    setIsConfirming(true);
    try {
      await reportsAPI.save(file.name, extractedData);
      navigate(`/dashboard`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to save finalized data.');
      setIsConfirming(false);
    }
  };

  const handleRetry = () => {
    setStage('uploading');
    setUploadPercent(0);
    setError(undefined);
    handleInitialAnalyze();
  };

  // Helper stats for visual review
  const totalTests = extractedData?.length || 0;
  const normalTests = extractedData?.filter(r => r.status === 'NORMAL').length || 0;
  const abnormalTests = extractedData?.filter(r => r.status === 'LOW' || r.status === 'HIGH').length || 0;
  const avgConfidence = Array.isArray(extractedData) && extractedData.length > 0
    ? Math.round((extractedData.reduce((acc, curr) => acc + (curr.ocr_confidence || 1), 0) / extractedData.length) * 100)
    : 100;

  // ── VIEW 2: Data Review & Verification Screen ──────────────────────────────
  if (extractedData) {
    return (
      <div className="max-w-6xl mx-auto py-6 px-4 animate-fade-in space-y-6">
        {/* Step Ribbon */}
        <div className="flex items-center justify-between bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500/10 text-primary-600 dark:text-primary-400 flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Review & Verify Extracted Results</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Source: <span className="font-medium text-gray-700 dark:text-gray-300">{file?.name}</span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setExtractedData(null)}
              className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
            >
              Re-upload File
            </button>
          </div>
        </div>

        {/* 4 Summary Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{totalTests}</div>
              <div className="text-xs text-gray-500">Total Tests Detected</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{normalTests}</div>
              <div className="text-xs text-gray-500">Normal Range</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{abnormalTests}</div>
              <div className="text-xs text-gray-500">Flags (Low / High)</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400 flex items-center justify-center">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold text-teal-600 dark:text-teal-400">{avgConfidence}%</div>
              <div className="text-xs text-gray-500">OCR Confidence</div>
            </div>
          </div>
        </div>

        {/* Extracted Data Table */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <div className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary-500" />
              Extracted Lab Biomarkers
            </div>
            <button 
              onClick={handleAddRow}
              className="text-xs flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-50 text-primary-600 hover:bg-primary-100 dark:bg-primary-900/30 dark:text-primary-400 font-medium transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> Add Missing Test
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/75 dark:bg-gray-900/40 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider font-semibold">
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Test Name</th>
                  <th className="px-4 py-3">Result Value</th>
                  <th className="px-4 py-3">Unit</th>
                  <th className="px-4 py-3">Reference Range</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50 text-sm">
                {extractedData.map((row) => {
                  const isHigh = row.status === 'HIGH';
                  const isLow = row.status === 'LOW';
                  const isNormal = row.status === 'NORMAL';

                  return (
                    <tr key={row.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-750 transition-colors">
                      {/* Status Pill */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                          isNormal ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300' :
                          isLow ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300' :
                          isHigh ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300' :
                          'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            isNormal ? 'bg-emerald-500' :
                            isLow ? 'bg-amber-500' :
                            isHigh ? 'bg-rose-500' : 'bg-gray-400'
                          }`} />
                          {row.status || 'NORMAL'}
                        </span>
                      </td>

                      {/* Test Name */}
                      <td className="px-4 py-3">
                        <input 
                          type="text" 
                          value={row.test_name} 
                          onChange={(e) => handleDataChange(row.id, 'test_name', e.target.value)}
                          className="input-field py-1.5 px-3 text-sm w-full font-medium"
                        />
                      </td>

                      {/* Value */}
                      <td className="px-4 py-3">
                        <input 
                          type="number" 
                          step="any"
                          value={row.value} 
                          onChange={(e) => handleDataChange(row.id, 'value', parseFloat(e.target.value))}
                          className="input-field py-1.5 px-3 text-sm w-28 font-semibold"
                        />
                      </td>

                      {/* Unit */}
                      <td className="px-4 py-3">
                        <input 
                          type="text" 
                          value={row.unit} 
                          placeholder="e.g. mg/dL"
                          onChange={(e) => handleDataChange(row.id, 'unit', e.target.value)}
                          className="input-field py-1.5 px-3 text-sm w-24 text-gray-600 dark:text-gray-300"
                        />
                      </td>

                      {/* Range */}
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <input 
                            type="number" 
                            step="any"
                            value={row.reference_low ?? ''} 
                            placeholder="Min"
                            onChange={(e) => handleDataChange(row.id, 'reference_low', e.target.value === '' ? null : parseFloat(e.target.value))}
                            className="input-field py-1.5 px-2.5 text-sm w-20 text-center"
                          />
                          <span className="text-gray-400">–</span>
                          <input 
                            type="number" 
                            step="any"
                            value={row.reference_high ?? ''} 
                            placeholder="Max"
                            onChange={(e) => handleDataChange(row.id, 'reference_high', e.target.value === '' ? null : parseFloat(e.target.value))}
                            className="input-field py-1.5 px-2.5 text-sm w-20 text-center"
                          />
                        </div>
                      </td>

                      {/* Delete */}
                      <td className="px-4 py-3 text-right">
                        <button 
                          onClick={() => handleRemoveRow(row.id)}
                          title="Remove Row"
                          className="p-1.5 text-gray-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-between pt-4">
          <button 
            onClick={() => setExtractedData(null)} 
            className="btn-secondary px-6 py-2.5 text-sm"
          >
            Cancel
          </button>
          <button 
            onClick={handleConfirmAndAnalyze} 
            disabled={isConfirming} 
            className="btn-primary px-8 py-3 text-sm font-semibold flex items-center gap-2 shadow-lg shadow-primary-500/20"
          >
            {isConfirming ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Saving & Analyzing...
              </>
            ) : (
              <>
                Confirm & Generate Health Insights <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // ── VIEW 1: Upload Dropzone & Initial State ────────────────────────────────
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 animate-fade-in space-y-8">
      {/* Visual Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5" /> High-Speed AI Extraction Pipeline
        </div>
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Upload Medical Report
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-lg mx-auto">
          Upload blood tests, metabolic panels, lipid profiles or diagnostic scans for instant analysis.
        </p>
      </div>

      {isProcessing ? (
        <div className="card p-8 bg-white dark:bg-gray-800 shadow-sm border border-gray-100 dark:border-gray-700">
          <UploadProgress 
            currentStage={stage} 
            uploadPercent={uploadPercent} 
            error={error} 
            onRetry={error ? handleRetry : undefined} 
          />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Visual Dropzone Card */}
          <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 border border-gray-100 dark:border-gray-700 shadow-sm">
            {!file ? (
              <FileDropZone onFileSelect={setFile} />
            ) : (
              <div className="space-y-6">
                <FilePreview file={file} onRemove={() => setFile(null)} />
                <div className="flex justify-center pt-2">
                  <button 
                    onClick={handleInitialAnalyze} 
                    className="btn-primary w-full sm:w-auto px-10 py-3.5 text-base font-semibold flex items-center justify-center gap-2 shadow-lg shadow-primary-500/25"
                  >
                    <Sparkles className="w-5 h-5" /> Scan & Extract Lab Results
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Privacy & Feature Guarantee Pills */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="flex items-center gap-3 p-4 rounded-2xl bg-white/60 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/60 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900 dark:text-white">HIPAA & Privacy Safe</h4>
                <p className="text-[11px] text-gray-500">Client-side document encryption</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-2xl bg-white/60 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/60 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400 flex items-center justify-center">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900 dark:text-white">Instant Reference Matching</h4>
                <p className="text-[11px] text-gray-500">Over 500+ lab ranges checked in &lt;1s</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-2xl bg-white/60 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/60 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                <ArrowRightLeft className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900 dark:text-white">Health Change Detection</h4>
                <p className="text-[11px] text-gray-500">Spot significant shifts between reports</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
