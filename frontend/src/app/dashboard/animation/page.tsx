"use client";

import { PageHeader } from '@/components/common/page-header';
import { SectionCard } from '@/components/common/section-card';
import { AnimationMap } from '@/features/animation/components/animation-map';
import { AnimationControls } from '@/features/animation/components/animation-controls';
import { AnimationTimeline } from '@/features/animation/components/animation-timeline';
import { AnimationInfoPanel } from '@/features/animation/components/animation-info-panel';
import { AnimationVariableSelector } from '@/features/animation/components/animation-variable-selector';
import { AnimationOrchestrator } from '@/features/animation/components/animation-orchestrator';
import { useInterpolationStore } from '@/store/interpolation-store';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function AnimationPage() {
  const { outputFileId } = useInterpolationStore();

  if (!outputFileId) {
    return (
      <div className="space-y-6">
        <PageHeader title="INSAT Time Evolution Viewer" description="Visualize atmospheric evolution over time and review temporal interpolations." />
        <div className="flex flex-col items-center justify-center min-h-[400px] border border-dashed border-slate-700 rounded-xl bg-slate-900/50 space-y-4 p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-2">
            <AlertCircle className="w-8 h-8 text-slate-400" />
          </div>
          <h3 className="text-xl font-semibold text-slate-200">No Interpolation Data</h3>
          <p className="text-slate-400 max-w-md">
            Generate an interpolation first to view the animation sequence. The animation viewer requires an established time-series.
          </p>
          <Link href="/dashboard/interpolation" className="mt-4">
            <Button>Go to Interpolation</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AnimationOrchestrator />
      <PageHeader title="INSAT Time Evolution Viewer" description="Visualize atmospheric evolution over time and review temporal interpolations." />
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <SectionCard>
            <AnimationMap />
          </SectionCard>
          
          <AnimationTimeline />
        </div>
        
        <div className="space-y-4">
          <AnimationVariableSelector />
          <AnimationControls />
          <AnimationInfoPanel />
        </div>
      </div>
    </div>
  );
}
