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

export function InterpolationWorkflowWrapper() {
  const { currentStep, nextStep, prevStep } = useInterpolationStore();
  const { jobState, updateConfig, startInterpolation, setInputFrame } = useInterpolation();

  const handleT0Upload = () => {
    // Mock upload success
    setInputFrame('t0', 't0_mock_id', 'T0_NetCDF.nc');
    nextStep();
  };

  const handleT1Upload = () => {
    // Mock upload success
    setInputFrame('t1', 't1_mock_id', 'T1_NetCDF.nc');
    nextStep();
  };

  const steps: Step[] = [
    {
      id: 1,
      label: 'Upload T0',
      description: 'First observation frame',
      component: (
        <div className="space-y-6">
          <UploadDropzone onUploadComplete={handleT0Upload} />
          {/* We would render actual metadata here when backend is ready */}
        </div>
      ),
    },
    {
      id: 2,
      label: 'Upload T1',
      description: 'Second observation frame',
      component: (
        <div className="space-y-6">
          <UploadDropzone onUploadComplete={handleT1Upload} />
        </div>
      ),
    },
    {
      id: 3,
      label: 'Process',
      description: 'AI Interpolation Engine',
      component: (
        <div className="space-y-8 max-w-2xl mx-auto">
          <InterpolationConfigPanel 
            config={jobState.config} 
            onConfigChange={updateConfig} 
          />
          <div className="flex justify-center pt-4">
            <Button 
              size="lg" 
              onClick={() => {
                startInterpolation();
                // Simulate processing delay for demo
                setTimeout(() => nextStep(), 3000);
              }}
              disabled={jobState.status === 'processing'}
              className="w-48 font-semibold shadow-lg"
            >
              {jobState.status === 'processing' ? 'Generating...' : 'Generate T0.5 Frame'}
            </Button>
          </div>
          <InterpolationTimeline status={jobState.status} />
          <InterpolationStatus jobState={jobState} />
        </div>
      ),
    },
    {
      id: 4,
      label: 'Result',
      description: 'Review and Export',
      component: (
        <div className="space-y-6">
          <InterpolationResultPreview jobState={jobState} />
          <div className="flex justify-center gap-4">
             <Button variant="outline" onClick={() => {
                // In a real app, this would route to validation or open export modal
                console.log('Proceeding to validation with artifact ID');
             }}>
               Proceed to Validation
             </Button>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto py-8">
      <WorkflowStepper steps={steps} currentStep={currentStep} />
      
      <div className="flex justify-between mt-8">
        <Button 
          variant="ghost" 
          onClick={prevStep} 
          disabled={currentStep === 1 || currentStep === 4}
        >
          Back
        </Button>
      </div>
    </div>
  );
}
