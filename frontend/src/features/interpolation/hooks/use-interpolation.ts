import { useState, useRef, useEffect } from 'react';
import { InterpolationJobState, InterpolationConfig } from '../types';
import { DEFAULT_INTERPOLATION_CONFIG } from '../constants';
import { interpolationClient, BASE_URL } from '@/lib/api';

const STORAGE_KEY = 'satellite-interpolation-job';

export function useInterpolation() {
  const [jobState, setJobState] = useState<InterpolationJobState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch (e) {
          console.error("Failed to parse saved job state", e);
        }
      }
    }
    return {
      status: 'idle',
      progress: 0,
      config: DEFAULT_INTERPOLATION_CONFIG,
      inputFrames: { t0: null, t1: null },
      outputFrame: null,
    };
  });

  const eventSourceRef = useRef<EventSource | null>(null);

  // Persist state changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(jobState));
  }, [jobState]);

  // Re-connect to SSE if we reloaded while processing
  useEffect(() => {
    if (jobState.status === 'processing' && jobState.jobId && !eventSourceRef.current) {
      connectSSE(jobState.jobId);
    }
    
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []); // Run once on mount

  const updateConfig = (newConfig: Partial<InterpolationConfig>) => {
    setJobState(prev => ({
      ...prev,
      config: { ...prev.config, ...newConfig }
    }));
  };

  const setInputFrame = (key: 't0' | 't1', id: string, filename: string) => {
    setJobState(prev => ({
      ...prev,
      inputFrames: {
        ...prev.inputFrames,
        [key]: { 
          id: id, 
          filename: filename, 
          timestamp: new Date().toISOString(),
          resolution: 'Metadata Pending'
        }
      }
    }));
  };

  const connectSSE = (jobId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const sseUrl = `${BASE_URL}${interpolationClient.getEventsUrl(jobId)}`;
    const eventSource = new EventSource(sseUrl);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        setJobState(prev => ({ ...prev, status: 'error', error: data.error }));
        eventSource.close();
        eventSourceRef.current = null;
        return;
      }

      setJobState(prev => ({ 
        ...prev, 
        progress: data.progress, 
        status: data.status 
      }));

      if (data.status === 'completed' || data.status === 'failed') {
        if (data.status === 'completed') {
          setJobState(prev => ({
            ...prev,
            outputFrame: {
              id: data.result_file_id,
              timestamp: new Date().toISOString(),
              resolution: 'Generated',
              dimensions: [0, 0],
              data: [],
              min: 0,
              max: 0
            } as any,
            completedAt: new Date().toISOString()
          }));
        }
        eventSource.close();
        eventSourceRef.current = null;
      }
    };

    eventSource.onerror = () => {
      console.error("SSE connection lost!");
      setJobState(prev => ({ ...prev, status: 'error', error: 'Connection to server lost. Still processing in cloud.' }));
      eventSource.close();
      eventSourceRef.current = null;
    };
  };

  const startInterpolation = async () => {
    const t0Id = jobState.inputFrames.t0?.id; 
    const t1Id = jobState.inputFrames.t1?.id;

    if (!t0Id || !t1Id) {
      alert("Bhai, pehle 2 files select karo interpolation ke liye!");
      return;
    }

    setJobState(prev => ({
      ...prev,
      status: 'preparing',
      progress: 0,
      startedAt: new Date().toISOString(),
      outputFrame: null,
      error: undefined,
    }));

    try {
      const res = await interpolationClient.generate(t0Id, t1Id, jobState.config.variable || "C13");
      
      if (!res.success) throw new Error(res.message);

      const jobId = res.data.job_id || res.data.jobId;
      setJobState(prev => ({ ...prev, status: 'processing', jobId }));

      connectSSE(jobId);
    } catch (error: any) {
      setJobState(prev => ({
        ...prev,
        status: 'error',
        error: error.message || 'Failed to generate interpolation frame.',
        completedAt: new Date().toISOString(),
      }));
    }
  };

  const resetJob = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setJobState(prev => ({
      ...prev,
      status: 'idle',
      progress: 0,
      outputFrame: null,
      jobId: undefined,
      startedAt: undefined,
      completedAt: undefined,
      error: undefined,
    }));
  };

  return {
    jobState,
    updateConfig,
    startInterpolation,
    resetJob,
    setInputFrame,
  };
}