'use client';

import React, { useState } from 'react';
import { useValidationStore } from '@/store/validation-store';
import { WorkflowStepper, Step } from '@/components/common/workflow-stepper';
import { UploadDropzone } from '@/features/upload/components/UploadDropzone';
import { MetadataOverview } from '@/features/metadata/components/metadata-overview';
import { ValidationViewer } from './validation-viewer';
import { MetricsDashboard } from '@/features/metrics/components/metrics-dashboard';
// Note: We use existing UI from other modules as requested.
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function ValidationWorkflowWrapper() {
  const { currentStep, nextStep, prevStep, setArtifactId, artifactId } = useValidationStore();
  const [tempArtifactId, setTempArtifactId] = useState('');

  const handleArtifactLoad = () => {
    setArtifactId(tempArtifactId);
    nextStep();
  };

  const handleGroundTruthUpload = () => {
    // Mock upload success
    nextStep();
  };

  const steps: Step[] = [
    {
      id: 1,
      label: 'Load Artifact',
      description: 'Fetch Generated T0.5',
      component: (
        <div className="space-y-6 max-w-xl mx-auto flex flex-col items-center justify-center h-full min-h-[300px]">
          <h2 className="text-xl font-semibold">Load Generated Frame</h2>
          <p className="text-muted-foreground text-center">
            Enter the Artifact ID of the interpolated frame generated in the previous workflow.
          </p>
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input 
              type="text" 
              placeholder="e.g. hf_artifact_9823" 
              value={tempArtifactId}
              onChange={(e) => setTempArtifactId(e.target.value)}
            />
            <Button onClick={handleArtifactLoad} disabled={!tempArtifactId}>Load</Button>
          </div>
        </div>
      ),
    },
    {
      id: 2,
      label: 'Ground Truth',
      description: 'Upload Actual T0.5',
      component: (
        <div className="space-y-6">
          <UploadDropzone onUploadComplete={handleGroundTruthUpload} />
        </div>
      ),
    },
    {
      id: 3,
      label: 'Metadata',
      description: 'Review Observation',
      component: (
        <div className="space-y-6">
          <div className="bg-muted/20 p-6 rounded-lg text-center">
            <p className="mb-4">Ground Truth Metadata loaded successfully.</p>
            <Button onClick={nextStep}>Proceed to Visual Inspection</Button>
          </div>
        </div>
      ),
    },
    {
      id: 4,
      label: 'Slider',
      description: 'AI vs Ground Truth',
      component: (
        <div className="space-y-6">
          <ValidationViewer 
            generatedImageUrl="/mock-images/generated.png" 
            groundTruthImageUrl="/mock-images/ground_truth.png" 
          />
          <div className="flex justify-center pt-4">
            <Button onClick={nextStep}>Analyze Difference Map</Button>
          </div>
        </div>
      ),
    },
    {
      id: 5,
      label: 'Difference',
      description: 'Spatial Error Map',
      component: (
        <div className="space-y-6">
           <div className="p-8 border-2 border-dashed border-border rounded-xl flex items-center justify-center min-h-[400px]">
              <p className="text-muted-foreground text-lg">Difference Map Module goes here</p>
           </div>
           <div className="flex justify-center pt-4">
            <Button onClick={nextStep}>Compute Metrics</Button>
          </div>
        </div>
      ),
    },
    {
      id: 6,
      label: 'Metrics',
      description: 'Quantitative Analysis',
      component: (
        <div className="space-y-6">
           <MetricsDashboard />
           <div className="flex justify-center pt-4">
            <Button onClick={nextStep}>Finalize Validation</Button>
          </div>
        </div>
      ),
    },
    {
      id: 7,
      label: 'Export',
      description: 'Validation Report',
      component: (
        <div className="space-y-6 flex flex-col items-center justify-center min-h-[300px]">
           <h2 className="text-2xl font-bold text-primary">Validation Complete!</h2>
           <p className="text-muted-foreground">The scientific evaluation pipeline has concluded.</p>
           <Button size="lg" className="mt-4">Download Validation Report</Button>
        </div>
      ),
    },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto py-8">
      <WorkflowStepper steps={steps} currentStep={currentStep} />
      
      <div className="flex justify-between mt-8">
        <Button 
          variant="ghost" 
          onClick={prevStep} 
          disabled={currentStep === 1 || currentStep === 7}
        >
          Back
        </Button>
      </div>
    </div>
  );
}
