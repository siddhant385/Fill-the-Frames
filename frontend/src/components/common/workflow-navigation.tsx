import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface WorkflowNavigationProps {
  currentStep: number;
  totalSteps: number;
  onPrev: () => void;
  onNext?: () => void;
  canGoNext?: boolean;
  canGoPrev?: boolean;
}

export function WorkflowNavigation({ 
  currentStep, 
  totalSteps, 
  onPrev, 
  onNext, 
  canGoNext = true,
  canGoPrev = true 
}: WorkflowNavigationProps) {
  return (
    <div className="flex items-center justify-between mt-8 border-t pt-6">
      <Button 
        variant="ghost" 
        onClick={onPrev} 
        disabled={currentStep === 1 || !canGoPrev}
        className="flex gap-2 text-muted-foreground hover:text-foreground"
      >
        <ChevronLeft className="w-4 h-4" />
        Back
      </Button>

      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, idx) => {
          const stepNumber = idx + 1;
          const isActive = stepNumber === currentStep;
          const isCompleted = stepNumber < currentStep;

          return (
            <div 
              key={idx}
              className={`h-2 rounded-full transition-all duration-300 ${
                isActive ? 'w-6 bg-primary' : 
                isCompleted ? 'w-2 bg-primary/50' : 'w-2 bg-muted'
              }`}
            />
          );
        })}
      </div>

      <Button 
        variant="ghost" 
        onClick={onNext} 
        disabled={currentStep === totalSteps || !canGoNext || !onNext}
        className={`flex gap-2 ${onNext ? 'text-primary hover:text-primary/80' : 'opacity-0 cursor-default'}`}
      >
        Next
        <ChevronRight className="w-4 h-4" />
      </Button>
    </div>
  );
}