import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { AlertTriangle, AlertCircle, Info, Stethoscope } from 'lucide-react';

interface PatternAlert {
  pattern_name: string;
  related_tests: string[];
  observed_values: string;
  explanation: string;
  severity: 'Low' | 'Medium' | 'High';
  recommended_discussion: string;
}

export const PatternsPage: React.FC = () => {
  const [patterns, setPatterns] = useState<PatternAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const res = await api.get('/results/patterns');
        setPatterns(res.data);
      } catch (err: any) {
        if (err.response?.status === 404 || err.code === 'ERR_NETWORK') {
          console.warn("API not ready, using mock data for /api/patterns");
          setPatterns([
            {
              pattern_name: 'Metabolic Syndrome Risk',
              related_tests: ['Glucose', 'Triglycerides', 'HDL Cholesterol'],
              observed_values: 'Glucose: 110 (High), Triglycerides: 160 (High), HDL: 35 (Low)',
              explanation: 'The combination of elevated fasting glucose, high triglycerides, and low HDL cholesterol is a classic presentation of metabolic syndrome.',
              severity: 'Medium',
              recommended_discussion: 'Discuss lifestyle modifications, dietary changes, and whether a hemoglobin A1c test is warranted.'
            },
            {
              pattern_name: 'Iron Deficiency Anemia',
              related_tests: ['Hemoglobin', 'Ferritin', 'MCV'],
              observed_values: 'Hemoglobin: 11.2 (Low), Ferritin: 12 (Low), MCV: 78 (Low)',
              explanation: 'Low hemoglobin alongside low ferritin and microcytic (low MCV) red blood cells strongly suggests iron deficiency.',
              severity: 'High',
              recommended_discussion: 'Ask your doctor about iron supplementation and potential causes of blood loss or malabsorption.'
            }
          ]);
        } else {
          setError(err.response?.data?.detail || 'Failed to load patterns');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchPatterns();
  }, []);

  if (loading) return <LoadingSpinner text="Analyzing biomarker patterns..." />;
  if (error) return <ErrorMessage message={error} />;

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'High': return 'border-red-500 bg-red-50 dark:bg-red-900/10 text-red-800 dark:text-red-300';
      case 'Medium': return 'border-amber-500 bg-amber-50 dark:bg-amber-900/10 text-amber-800 dark:text-amber-300';
      case 'Low': return 'border-blue-500 bg-blue-50 dark:bg-blue-900/10 text-blue-800 dark:text-blue-300';
      default: return 'border-gray-500 bg-gray-50 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch(severity) {
      case 'High': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'Medium': return <AlertCircle className="w-5 h-5 text-amber-500" />;
      case 'Low': return <Info className="w-5 h-5 text-blue-500" />;
      default: return null;
    }
  };

  return (
    <div className="p-6 animate-fade-in max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Biomarker Pattern Engine</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-6">AI-detected health patterns across multiple test results.</p>
      
      {patterns.length === 0 ? (
        <div className="text-center p-8 card text-gray-500">
          No patterns detected based on your current data.
        </div>
      ) : (
        <div className="space-y-6">
          {patterns.map((pattern, idx) => (
            <div key={idx} className={`border-l-4 rounded-r-xl shadow-sm p-5 ${getSeverityColor(pattern.severity)}`}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold flex items-center gap-2">
                    {getSeverityIcon(pattern.severity)}
                    {pattern.pattern_name}
                  </h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {pattern.related_tests.map(test => (
                      <span key={test} className="bg-white/60 dark:bg-gray-800/60 px-2 py-1 rounded text-xs font-semibold shadow-sm">
                        {test}
                      </span>
                    ))}
                  </div>
                </div>
                <span className="text-xs font-bold uppercase tracking-wider opacity-80">
                  {pattern.severity} Severity
                </span>
              </div>
              
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-semibold opacity-80 mb-1">Observed Values:</p>
                  <p>{pattern.observed_values}</p>
                </div>
                <div>
                  <p className="font-semibold opacity-80 mb-1">Clinical Explanation:</p>
                  <p>{pattern.explanation}</p>
                </div>
              </div>
              
              <div className="mt-5 pt-4 border-t border-black/10 dark:border-white/10 flex items-start gap-3">
                <div className="bg-white/50 dark:bg-black/20 p-2 rounded-full">
                  <Stethoscope className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-semibold text-sm opacity-80">Recommended Discussion Point:</p>
                  <p className="text-sm italic mt-1">"{pattern.recommended_discussion}"</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
