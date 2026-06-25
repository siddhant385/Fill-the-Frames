"use client";

import React, { useImperativeHandle, forwardRef, useState } from 'react';
import { ColorMap } from '../types';
import { BASE_URL } from '@/lib/api';

interface SatelliteViewerProps {
  layerUrl?: string | null;
  colorMap: ColorMap;
  onHover?: (e: any) => void;
  onUnhover?: () => void;
  data?: any; // kept for compatibility with existing props
}

export interface SatelliteViewerRef {
  resetView: () => void;
}

export const SatelliteViewer = forwardRef<SatelliteViewerRef, SatelliteViewerProps>(
  ({ layerUrl, colorMap }, ref) => {
    const [zoom, setZoom] = useState(1);
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [startDrag, setStartDrag] = useState({ x: 0, y: 0 });

    useImperativeHandle(ref, () => ({
      resetView: () => {
        setZoom(1);
        setPan({ x: 0, y: 0 });
      }
    }));

    if (!layerUrl) {
       return (
         <div className="w-full h-full min-h-[400px] md:min-h-[600px] flex items-center justify-center border rounded-lg overflow-hidden bg-background">
           <p className="text-muted-foreground">No layer data available</p>
         </div>
       );
    }

    const fullUrl = layerUrl.startsWith('http') ? layerUrl : `${BASE_URL}${layerUrl}`;

    return (
      <div className="relative w-full h-full min-h-[400px] md:min-h-[600px] border rounded-lg overflow-hidden bg-background/50 flex flex-col items-center justify-center">
        <div 
          className="relative w-full h-full overflow-hidden flex items-center justify-center"
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
          <img 
            src={fullUrl} 
            alt="Satellite Data Layer" 
            className="max-w-full max-h-full object-contain pointer-events-none"
            style={{ 
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center'
            }}
            crossOrigin="anonymous"
          />
        </div>
        
        {/* Simple zoom controls overlay */}
        <div className="absolute bottom-4 right-4 flex gap-2 bg-background/80 backdrop-blur rounded-md border p-1 shadow-sm">
           <button onClick={() => setZoom(z => Math.min(z + 0.5, 5))} className="w-8 h-8 flex items-center justify-center hover:bg-secondary rounded text-sm font-medium">+</button>
           <button onClick={() => { setZoom(1); setPan({x:0, y:0}); }} className="px-2 h-8 flex items-center justify-center hover:bg-secondary rounded text-xs font-medium text-muted-foreground">Reset</button>
           <button onClick={() => setZoom(z => Math.max(z - 0.5, 0.5))} className="w-8 h-8 flex items-center justify-center hover:bg-secondary rounded text-sm font-medium">-</button>
        </div>
      </div>
    );
  }
);
SatelliteViewer.displayName = 'SatelliteViewer';