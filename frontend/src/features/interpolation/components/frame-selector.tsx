import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Clock, File as FileIcon } from 'lucide-react';
import { useUploadStore } from '@/store/upload-store';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface FramePreviewCardProps {
  label: string;
  frame: any; // Temporarily any, jab tak proper type na set ho
  onSelect: (cloudId: string, filename: string) => void;
}

function FramePreviewCard({ label, frame, onSelect }: FramePreviewCardProps) {
  // 🚨 FIX: Zustand hook me direct filter() hatakar seedha array nikala hai taaki Infinite Loop na bane!
  const allFiles = useUploadStore((state) => state.files);
  
  // Ab nikalne ke baad usko yahan component me filter kar lo
  const completedFiles = allFiles.filter(f => f.status === 'completed' && f.cloudFileId);

  return (
    <Card className="flex-1 bg-muted/10 border-dashed">
      <CardHeader className="pb-2">
        <CardTitle className="text-md text-center">{label}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        
        <Select onValueChange={(val) => {
          const selected = completedFiles.find(f => f.cloudFileId === val);
          if (selected) onSelect(val, selected.file.name);
        }}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select uploaded file..." />
          </SelectTrigger>
          <SelectContent>
            {completedFiles.length === 0 ? (
              <SelectItem value="none" disabled>No completed uploads found</SelectItem>
            ) : (
              completedFiles.map(file => (
                <SelectItem key={file.cloudFileId!} value={file.cloudFileId!}>
                  {file.file.name}
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>

        {frame ? (
          <div className="space-y-3">
            <div className="w-full aspect-square bg-muted rounded flex flex-col items-center justify-center text-muted-foreground border">
              <FileIcon className="w-8 h-8 mb-2 opacity-50" />
              <span className="text-xs font-mono px-2 text-center break-all">
                {frame.filename || 'File Selected'}
              </span>
            </div>
            <div className="flex flex-col gap-1 text-sm text-center">
              <div className="flex items-center justify-center gap-1 text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span className="text-xs truncate max-w-[150px]">{frame.id}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-[180px] flex items-center justify-center text-sm text-muted-foreground py-8">
            Please select a file
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface FrameSelectorProps {
  t0: any;
  t1: any;
  onSelectT0: (id: string, filename: string) => void;
  onSelectT1: (id: string, filename: string) => void;
}

export function FrameSelector({ t0, t1, onSelectT0, onSelectT1 }: FrameSelectorProps) {
  return (
    <div className="flex flex-col md:flex-row gap-6 w-full max-w-3xl mx-auto">
      <FramePreviewCard 
        label="T0 (Start Frame)" 
        frame={t0} 
        onSelect={onSelectT0} 
      />
      <FramePreviewCard 
        label="T1 (End Frame)" 
        frame={t1} 
        onSelect={onSelectT1} 
      />
    </div>
  );
}