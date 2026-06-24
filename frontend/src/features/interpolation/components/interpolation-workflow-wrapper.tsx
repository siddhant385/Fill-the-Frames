'use client';

import React from 'react';
import { useInterpolationStore } from '@/store/interpolation-store';
import { WorkflowStepper, Step } from '@/components/common/workflow-stepper';
import { UploadDropzone } from '@/features/upload/components/UploadDropzone';
import { MetadataOverview } from '@/features/metadata/components/metadata-overview';
import { InterpolationConfigPanel } from './interpolation-config-panel';
import { InterpolationTimeline } from './interpolation-timeline';
import { InterpolationStatus } from './interpolation-status';
import { InterpolationResultPreview } from './interpolation-result-preview';
import { Button } from '@/components/ui/button';
import { useInterpolation } from '../hooks/use-interpolation';
import { DetailedSatelliteMetadata } from '@/features/metadata/types';

const dummyMetadata = {
  id: 'dummy',
  timestamp: new Date().toISOString(),
  satelliteId: 'INSAT-3D',
  productType: 'L1B',
  processingLevel: 'L1',
  spatialResolution: '1km',
  bandName: 'TIR1',
  centralWavelength: '10.8um',
  projection: 'Mercator',
  bounds: [0, 0, 0, 0],
  fileSize: 0,
  dimensions: [],
  variables: [],
  coordinates: []
} as unknown as DetailedSatelliteMetadata;

export function InterpolationWorkflowWrapper() {
  const store = useInterpolationStore();
  const { startInterpolation } = useInterpolation();

  const handleT0Upload = () => {
    store.setInputFrame('t0', { 
      id: 't0_mock_id', 
      filename: 'T0_NetCDF.nc',
      timestamp: new Date().toISOString(),
      resolution: 'Mock',
      dimensions: [0, 0],
      data: [],
      min: 0,
      max: 0
    });
    store.nextStep();
  };

  const handleT1Upload = () => {
    store.setInputFrame('t1', { 
      id: 't1_mock_id', 
      filename: 'T1_NetCDF.nc',
      timestamp: new Date().toISOString(),
      resolution: 'Mock',
      dimensions: [0, 0],
      data: [],
      min: 0,
      max: 0
    });
    store.nextStep();
  };

  const steps: Step[] = [
    {
      id: 1,
      label: 'Upload T0',
      description: 'First observation frame',
      component: (
        <div className="space-y-6">
          <UploadDropzone onUploadComplete={handleT0Upload} />
        </div>
      ),
    },
    {
      id: 2,
      label: 'Review T0',
      description: 'Review T0 Metadata',
      component: (
        <div className="space-y-6">
          <MetadataOverview data={dummyMetadata} />
          <div className="flex justify-center pt-4">
            <Button onClick={store.nextStep}>Proceed to T1 Upload</Button>
          </div>
        </div>
      ),
    },
    {
      id: 3,
      label: 'Upload T1',
      description: 'Second observation frame',
      component: (
        <div className="space-y-6">
          <UploadDropzone onUploadComplete={handleT1Upload} />
        </div>
      ),
    },
    {
      id: 4,
      label: 'Review T1',
      description: 'Review T1 Metadata',
      component: (
        <div className="space-y-6">
          <MetadataOverview data={dummyMetadata} />
          <div className="flex justify-center pt-4">
            <Button onClick={store.nextStep}>Proceed to Configuration</Button>
          </div>
        </div>
      ),
    },
    {
      id: 5,
      label: 'Process',
      description: 'Run Interpolation',
      component: (
        <div className="space-y-8 max-w-2xl mx-auto">
          <InterpolationConfigPanel 
            config={store.config} 
            onConfigChange={store.updateConfig} 
          />
          <div className="flex justify-center pt-4">
            <Button 
              size="lg" 
              onClick={() => {
                startInterpolation();
                // Simulate processing delay for demo
                setTimeout(() => store.nextStep(), 3000);
              }}
              disabled={store.status === 'processing'}
              className="w-48 font-semibold shadow-lg"
            >
              {store.status === 'processing' ? 'Generating...' : 'Generate T0.5 Frame'}
            </Button>
          </div>
          <InterpolationTimeline status={store.status} />
          <InterpolationStatus jobState={store} />
        </div>
      ),
    },
    {
      id: 6,
      label: 'Result',
      description: 'Generated T0.5',
      component: (
        <div className="space-y-6">
          <InterpolationResultPreview jobState={store} />
          <div className="flex justify-center gap-4">
             <Button variant="outline" onClick={() => {
                store.nextStep();
             }}>
               Review Export Options
             </Button>
          </div>
        </div>
      ),
    },
    {
      id: 7,
      label: 'Export',
      description: 'Export Result',
      component: (
        <div className="space-y-6 flex flex-col items-center justify-center min-h-[300px]">
           <h2 className="text-2xl font-bold text-primary">Export Options</h2>
           <p className="text-muted-foreground">Download the generated T0.5 frame.</p>
           <Button size="lg" className="mt-4">Download .nc File</Button>
        </div>
      ),
    },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto py-8">
      <WorkflowStepper steps={steps} currentStep={store.currentStep} />
      
      <div className="flex justify-between mt-8">
        <Button 
          variant="ghost" 
          onClick={store.prevStep} 
          disabled={store.currentStep === 1 || store.currentStep === 7}
        >
          Back
        </Button>
      </div>
    </div>
  );
}
