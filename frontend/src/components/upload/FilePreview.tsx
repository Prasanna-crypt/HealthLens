// Just a standard component, nothing fancy here.

import React from 'react';

interface Props {
  file: File;
  onRemove: () => void;
}

export const FilePreview: React.FC<Props> = ({ file, onRemove }) => {
  // Check if it's an image (so we can show a thumbnail) or a PDF
  const isImage = file.type.startsWith('image/');
  
  // Convert bytes to Megabytes
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
  
  // Create a temporary image URL for preview, only if it's an image
  const objectUrl = React.useMemo(() => {
    if (isImage) return URL.createObjectURL(file);
    return null;
  }, [file, isImage]);

  return (
    <div className="card p-4 flex items-center justify-between mt-6">
      <div className="flex items-center space-x-4">
        
        {/* Show image thumbnail or a generic PDF icon */}
        {isImage && objectUrl ? (
          <img src={objectUrl} alt="Preview" className="w-16 h-16 object-cover rounded-lg border border-gray-200 dark:border-gray-700" />
        ) : (
          <div className="w-16 h-16 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-500 flex items-center justify-center border border-red-200 dark:border-red-800">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        
        {/* File details */}
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-[200px] sm:max-w-xs">{file.name}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{sizeMB} MB • {isImage ? 'Image' : 'PDF'}</p>
        </div>
      </div>
      
      {/* Remove button */}
      <button onClick={onRemove} className="p-2 text-gray-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-full transition-colors">
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};
