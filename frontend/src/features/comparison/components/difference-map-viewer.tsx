"use client";

import React, { useState } from 'react';
import type { Layout, PlotRelayoutEvent } from 'plotly.js';
import { DifferenceMapData } from '../types';
import { BASE_URL } from '@/lib/api';

interface DifferenceMapViewerProps {
  differenceMap: DifferenceMapData;
  errorMapUrl?: string | null;
  sharedLayout: Partial<Layout>;
  onRelayout: (eventData: Readonly<PlotRelayoutEvent>) => void;
  isFullscreen: boolean;
}

export function DifferenceMapViewer({ 
  differenceMap, 
  errorMapUrl,
  sharedLayout, 
  onRelayout,
  isFullscreen 
}: DifferenceMapViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [startDrag, setStartDrag] = useState({ x: 0, y: 0 });

  const heightClass = isFullscreen ? 'h-[80vh]' : 'h-[60vh] min-h-[500px]';

  const fullUrl = errorMapUrl 
    ? (errorMapUrl.startsWith('http') ? errorMapUrl : `${BASE_URL}${errorMapUrl}`) 
    : null;

  return (
    <div className={`w-full ${heightClass} border rounded-lg overflow-hidden bg-background relative flex flex-col`}>
      <div className="absolute top-4 left-4 z-10 bg-background/90 backdrop-blur px-3 py-2 rounded text-sm font-semibold shadow-md border">
        {differenceMap.band} (Error/Diff Map)
      </div>

      <div className="flex-1 w-full relative flex items-center justify-center bg-background/50 overflow-hidden"
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
            alt="Difference Map" 
            className="max-w-full max-h-full object-contain pointer-events-none transition-transform duration-75"
            style={{ 
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center'
            }}
            crossOrigin="anonymous"
          />
        ) : (
          <div className="text-muted-foreground flex flex-col items-center">
             <span>Error map layer not available.</span>
             <span className="text-xs mt-1 opacity-70">Ensure 2 files are uploaded and processed.</span>
          </div>
        )}
      </div>

      <div className="absolute bottom-4 right-4 flex gap-2 bg-background/80 backdrop-blur rounded-md border p-1 shadow-sm">
           <button onClick={() => setZoom(z => Math.min(z + 0.5, 5))} className="w-8 h-8 flex items-center justify-center hover:bg-secondary rounded text-sm font-medium">+</button>
           <button onClick={() => { setZoom(1); setPan({x:0, y:0}); }} className="px-2 h-8 flex items-center justify-center hover:bg-secondary rounded text-xs font-medium text-muted-foreground">Reset</button>
           <button onClick={() => setZoom(z => Math.max(z - 0.5, 0.5))} className="w-8 h-8 flex items-center justify-center hover:bg-secondary rounded text-sm font-medium">-</button>
      </div>
    </div>
  );
}