import React from 'react';
import { UploadDropzone } from '@/features/upload/components/UploadDropzone';

export default function UploadPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Upload Data</h2>
      </div>
      
      <div className="w-full max-w-4xl mx-auto mt-8">
        <UploadDropzone />
      </div>
    </div>
  );
}
