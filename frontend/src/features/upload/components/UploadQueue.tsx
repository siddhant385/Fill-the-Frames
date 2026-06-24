'use client';

import { useUploadStore } from '@/store/upload-store';
import { UploadCard } from './UploadCard';
import { AnimatePresence, motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Trash2, PlayCircle, Play } from 'lucide-react';

export function UploadQueue() {
  const { files, clearCompleted, startAllReadyUploads } = useUploadStore();

  if (files.length === 0) return null;

  const hasReadyFiles = files.some(f => f.status === 'ready');
  const hasCompletedFiles = files.some(f => f.status === 'completed');

  return (
    <div className="w-full mt-6 flex flex-col gap-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          Upload Queue
          <span className="text-sm font-normal text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            {files.length} files
          </span>
        </h3>
        
        <div className="flex gap-2">
          {hasReadyFiles && (
            <Button size="sm" onClick={startAllReadyUploads} className="gap-2">
              <Play className="h-4 w-4" />
              Upload All
            </Button>
          )}
          {hasCompletedFiles && (
            <Button size="sm" variant="ghost" onClick={clearCompleted} className="text-muted-foreground hover:text-destructive">
              <Trash2 className="h-4 w-4 mr-2" /> Clear Completed
            </Button>
          )}
        </div>
      </div>
      
      <motion.div layout className="grid gap-3">
        <AnimatePresence mode="popLayout">
          {files.map((file) => (
            <UploadCard key={file.id} fileData={file} />
          ))}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
