import { create } from 'zustand';
import { InterpolationJobState, InterpolationConfig, MockFrame } from '@/features/interpolation/types';
import { DEFAULT_INTERPOLATION_CONFIG } from '@/features/interpolation/constants';

interface InterpolationState extends InterpolationJobState {
  currentStep: number;
  
  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  
  setJobState: (state: Partial<InterpolationJobState>) => void;
  updateConfig: (config: Partial<InterpolationConfig>) => void;
  setInputFrame: (key: 't0' | 't1', frame: MockFrame) => void;
  reset: () => void;
}

const initialState: InterpolationJobState = {
  status: 'idle',
  progress: 0,
  config: DEFAULT_INTERPOLATION_CONFIG,
  inputFrames: {
    t0: null,
    t1: null,
  },
  outputFrame: null,
};

export const useInterpolationStore = create<InterpolationState>((set) => ({
  currentStep: 1,
  ...initialState,
  
  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  prevStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) })),
  
  setJobState: (newState) => set((state) => ({ ...state, ...newState })),
  
  updateConfig: (newConfig) => set((state) => ({
    config: { ...state.config, ...newConfig }
  })),
  
  setInputFrame: (key, frame) => set((state) => ({
    inputFrames: {
      ...state.inputFrames,
      [key]: frame
    }
  })),

  reset: () => set({
    currentStep: 1,
    ...initialState,
    jobId: undefined,
    startedAt: undefined,
    completedAt: undefined,
    error: undefined,
  }),
}));
