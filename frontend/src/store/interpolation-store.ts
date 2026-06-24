import { create } from 'zustand';

interface InterpolationState {
  currentStep: number;
  t0FileId: string | null;
  t1FileId: string | null;
  isProcessing: boolean;
  generatedArtifactId: string | null;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setT0FileId: (id: string | null) => void;
  setT1FileId: (id: string | null) => void;
  setIsProcessing: (processing: boolean) => void;
  setGeneratedArtifactId: (id: string | null) => void;
  reset: () => void;
}

export const useInterpolationStore = create<InterpolationState>((set) => ({
  currentStep: 1,
  t0FileId: null,
  t1FileId: null,
  isProcessing: false,
  generatedArtifactId: null,
  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  prevStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) })),
  setT0FileId: (id) => set({ t0FileId: id }),
  setT1FileId: (id) => set({ t1FileId: id }),
  setIsProcessing: (processing) => set({ isProcessing: processing }),
  setGeneratedArtifactId: (id) => set({ generatedArtifactId: id }),
  reset: () => set({
    currentStep: 1,
    t0FileId: null,
    t1FileId: null,
    isProcessing: false,
    generatedArtifactId: null,
  }),
}));
