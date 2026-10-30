import React from 'react';
import { Shield, Lock, EyeOff, FileText, Database } from 'lucide-react';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 animate-fade-in space-y-8">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 mb-4">
          <Shield className="w-8 h-8 text-primary-600 dark:text-primary-400" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Privacy & Consent</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-2xl mx-auto">
          We take your health data seriously. Understand how HealthLens protects, processes, and respects your privacy.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6 space-y-4">
          <Lock className="w-8 h-8 text-indigo-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Data Storage & Encryption</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            All medical records and extracted biomarker data are encrypted both in transit and at rest using AES-256 standards. Your data is stored in secure, compliance-ready infrastructure.
          </p>
        </div>

        <div className="card p-6 space-y-4">
          <EyeOff className="w-8 h-8 text-emerald-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI Processing Notice</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            HealthLens uses advanced AI to extract and analyze data from your reports. Personally Identifiable Information (PII) is obfuscated locally on your device before text is sent to the LLM for analysis.
          </p>
        </div>

        <div className="card p-6 space-y-4">
          <FileText className="w-8 h-8 text-amber-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Consent Parameters</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            By using HealthLens, you consent to the parsing of your uploaded lab reports for the sole purpose of generating personal insights. We do not sell your health data to third parties.
          </p>
        </div>

        <div className="card p-6 space-y-4">
          <Database className="w-8 h-8 text-rose-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Export & Delete Options</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            You maintain full ownership of your data. You can request a complete export of your digital records or permanently delete your account and all associated data at any time via Settings.
          </p>
        </div>
      </div>
      
      <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700 text-center">
        <p className="text-xs text-gray-400">Last Updated: September 2026. For questions regarding privacy practices, please contact privacy@healthlens.example.com</p>
      </div>
    </div>
  );
};
