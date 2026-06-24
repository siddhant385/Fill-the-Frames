'use client';

import React from 'react';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';

interface ValidationViewerProps {
  generatedImageUrl: string;
  groundTruthImageUrl: string;
}

export function ValidationViewer({ generatedImageUrl, groundTruthImageUrl }: ValidationViewerProps) {
  return (
    <div className="w-full max-w-4xl mx-auto rounded-lg overflow-hidden border border-border shadow-md">
      <ReactCompareSlider
        itemOne={
          <ReactCompareSliderImage 
            src={generatedImageUrl} 
            alt="AI Generated (T0.5)" 
          />
        }
        itemTwo={
          <ReactCompareSliderImage 
            src={groundTruthImageUrl} 
            alt="Ground Truth (Actual T0.5)" 
          />
        }
        className="h-[500px] w-full"
      />
      <div className="flex justify-between p-4 bg-muted/30 text-sm font-medium">
        <span className="text-primary">AI Generated (T0.5)</span>
        <span className="text-muted-foreground">Ground Truth (Actual T0.5)</span>
      </div>
    </div>
  );
}
