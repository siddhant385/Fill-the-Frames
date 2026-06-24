import { create } from 'zustand';

interface ValidationState {
  currentStep: number;
  artifactId: string | null; // loaded generated T0.5
  groundTruthFileId: string | null;
  metricsComputed: boolean;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setArtifactId: (id: string | null) => void;
  setGroundTruthFileId: (id: string | null) => void;
  setMetricsComputed: (computed: boolean) => void;
  reset: () => void;
}

export const useValidationStore = create<ValidationState>((set) => ({
  currentStep: 1,
  artifactId: null,
  groundTruthFileId: null,
  metricsComputed: false,
  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  prevStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) })),
  setArtifactId: (id) => set({ artifactId: id }),
  setGroundTruthFileId: (id) => set({ groundTruthFileId: id }),
  setMetricsComputed: (computed) => set({ metricsComputed: computed }),
  reset: () => set({
    currentStep: 1,
    artifactId: null,
    groundTruthFileId: null,
    metricsComputed: false,
  }),
}));
