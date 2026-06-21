import { useState, useEffect } from 'react';
import { DetailedSatelliteMetadata, MetadataState } from '../types';
import { mockMetadata } from '../mock/data';

/**
 * Hook to manage metadata state and fetching.
 * Currently returns mock data, but designed to connect to global stores or APIs in the future.
 */
export function useMetadata(initialData?: DetailedSatelliteMetadata) {
  const [data, setData] = useState<DetailedSatelliteMetadata | null>(initialData || null);
  const [state, setState] = useState<MetadataState>(initialData ? 'ready' : 'loading');

  useEffect(() => {
    if (initialData) {
      setData(initialData);
      setState('ready');
      return;
    }

    // Simulate an async operation (e.g., parsing a NetCDF file or calling a backend API)
    const loadMetadata = async () => {
      try {
        setState('loading');
        // Simulated delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // In the future, this would check `useUploadStore.getState().selectedFileMetadata`
        setData(mockMetadata);
        setState('ready');
      } catch (error) {
        setState('error');
      }
    };

    loadMetadata();
  }, [initialData]);

  return {
    data,
    state,
  };
}
