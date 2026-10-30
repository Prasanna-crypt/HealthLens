// Just a standard component, nothing fancy here.

import React, { useCallback, useState } from 'react';

interface FileDropZoneProps {
  onFileSelect: (file: File) => void;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({ onFileSelect }) => {
  // Track if a file is currently hovering over the zone
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault(); // Required to allow dropping
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false); // User dragged the file away
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    // If files were dropped, pass the first one up to the parent component
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  // Fallback for clicking the zone instead of dragging
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div
      // Change styles if a file is hovering (isDragging)
      className={`relative border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center text-center transition-all duration-300 ${
        isDragging
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 dark:border-gray-700 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Invisible file input covering the whole area */}
      <input
        type="file"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={handleChange}
        accept=".pdf,.jpg,.jpeg,.png"
      />
      
      <div className={`w-16 h-16 mb-4 rounded-full flex items-center justify-center ${isDragging ? 'bg-primary-100 dark:bg-primary-900 text-primary-600' : 'bg-gray-100 dark:bg-gray-800 text-gray-500'} transition-colors`}>
        <svg className={`w-8 h-8 ${isDragging ? 'animate-bounce' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-navy-700 dark:text-white mb-2">Drag and drop your medical report</h3>
      <p className="text-gray-500 dark:text-gray-400 mb-6">or click to browse</p>
      <div className="text-sm text-gray-400 dark:text-gray-500">
        Supported formats: JPG, JPEG, PNG, PDF (up to 10MB)
      </div>
    </div>
  );
};
