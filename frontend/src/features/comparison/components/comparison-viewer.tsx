"use client";

import React, { useState } from 'react';
import type { Layout, PlotRelayoutEvent } from 'plotly.js';
import { ComparisonFrame } from '../types';
import { formatDate } from '@/features/metadata/utils/formatters';
import { BASE_URL } from '@/lib/api';

interface ComparisonViewerProps {
  frame: ComparisonFrame;
  layerUrl?: string | null;
  sharedLayout: Partial<Layout>;
  onRelayout: (eventData: Readonly<PlotRelayoutEvent>) => void;
  colormap?: string;
  hideMetadata?: boolean;
}

export function ComparisonViewer({ 
  frame, 
  layerUrl,
  sharedLayout, 
  onRelayout,
  colormap = 'Inferno',
  hideMetadata = false
}: ComparisonViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [startDrag, setStartDrag] = useState({ x: 0, y: 0 });

  const fullUrl = layerUrl 
    ? (layerUrl.startsWith('http') ? layerUrl : `${BASE_URL}${layerUrl}`) 
    : null;
  
  return (
    <div className="flex flex-col h-full bg-muted/5 border rounded-lg overflow-hidden relative">
      <div className="absolute top-2 left-2 z-10 bg-background/80 backdrop-blur px-2 py-1 rounded text-xs font-semibold shadow-sm border">
        {frame.type}
      </div>
      
      <div className="flex-1 w-full relative min-h-[300px] flex items-center justify-center overflow-hidden bg-background/50"
          onMouseDown={(e) => {
            setIsDragging(true);
            setStartDrag({ x: e.clientX - pan.x, y: e.clientY - pan.y });
          }}
          onMouseMove={(e) => {
            if (!isDragging) return;
            setPan({ x: e.clientX - startDrag.x, y: e.clientY - startDrag.y });
          }}
          onMouseUp={() => setIsDragging(false)}
          onMouseLeave={() => setIsDragging(false)}
          style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        {fullUrl ? (
          <img 
            src={fullUrl} 
            alt="Satellite View" 
            className="max-w-full max-h-full object-contain pointer-events-none transition-transform duration-75"
            style={{ 
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center'
            }}
            crossOrigin="anonymous"
          />
        ) : (
          <div className="text-muted-foreground text-sm opacity-60 flex flex-col items-center">
             <span>Layer not available</span>
             <span className="text-xs">Using placeholder</span>
          </div>
        )}
      </div>

      <div className="absolute bottom-16 right-2 flex gap-1 bg-background/80 backdrop-blur rounded border p-1 shadow-sm opacity-50 hover:opacity-100 transition-opacity">
           <button onClick={() => setZoom(z => Math.min(z + 0.5, 5))} className="w-6 h-6 flex items-center justify-center hover:bg-secondary rounded text-xs font-medium">+</button>
           <button onClick={() => { setZoom(1); setPan({x:0, y:0}); }} className="px-1 h-6 flex items-center justify-center hover:bg-secondary rounded text-[10px] font-medium text-muted-foreground">Reset</button>
           <button onClick={() => setZoom(z => Math.max(z - 0.5, 0.5))} className="w-6 h-6 flex items-center justify-center hover:bg-secondary rounded text-xs font-medium">-</button>
      </div>

      {!hideMetadata && (
        <div className="p-3 bg-muted/20 border-t text-xs grid grid-cols-2 gap-2">
          <div className="flex flex-col">
            <span className="text-muted-foreground uppercase text-[10px]">Timestamp</span>
            <span className="font-medium truncate">{formatDate(frame.timestamp)}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground uppercase text-[10px]">Band</span>
            <span className="font-medium truncate">{frame.band}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground uppercase text-[10px]">Resolution</span>
            <span className="font-medium truncate">{frame.resolution}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground uppercase text-[10px]">Dimensions</span>
            <span className="font-medium truncate">{frame.dimensions.join(' × ')}</span>
          </div>
        </div>
      )}
    </div>
  );
}