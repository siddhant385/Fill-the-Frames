import { useState, useCallback, useEffect } from 'react';
import type { Layout, PlotRelayoutEvent } from 'plotly.js';
import { syncPlotlyRelayout } from '@/utils/plotly-events';
import { ComparisonMode, ComparisonState } from '../types';
import { DEFAULT_COMPARISON_MODE } from '../constants';
import { MOCK_COMP_T0, MOCK_COMP_T1, MOCK_COMP_T05, MOCK_DIFFERENCE_MAP } from '../mock/data';
import { useUploadStore } from '@/store/upload-store';
import { visualizationClient } from '@/lib/api';

export function useComparison() {
  const [state, setState] = useState<ComparisonState>('ready');
  const [mode, setMode] = useState<ComparisonMode>(DEFAULT_COMPARISON_MODE);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [errorMapUrl, setErrorMapUrl] = useState<string | null>(null);

  const files = useUploadStore(state => state.files);

  // Shared layout state for linked pan/zoom
  const [sharedLayout, setSharedLayout] = useState<Partial<Layout>>({});

  useEffect(() => {
    // Generate error map url
    const completedFiles = files.filter(f => f.status === 'completed' && f.cloudFileId);
    if (completedFiles.length >= 2) {
      const url = visualizationClient.getErrorMapLayerUrl(
        completedFiles[0].cloudFileId!, 
        completedFiles[1].cloudFileId!, 
        "C13", 
        0
      );
      setErrorMapUrl(url);
    }
  }, [files]);

  const handleRelayout = useCallback((eventData: Readonly<PlotRelayoutEvent>) => {
    syncPlotlyRelayout(eventData, setSharedLayout);
  }, []);

  const resetView = useCallback(() => {
    setSharedLayout({
      xaxis: { autorange: true },
      yaxis: { autorange: true },
    });
  }, []);

  return {
    state,
    mode,
    setMode,
    isFullscreen,
    toggleFullscreen: () => setIsFullscreen(!isFullscreen),
    sharedLayout,
    handleRelayout,
    resetView,
    errorMapUrl,
    frames: {
      t0: MOCK_COMP_T0,
      t1: MOCK_COMP_T1,
      t05: MOCK_COMP_T05,
    },
    differenceMap: MOCK_DIFFERENCE_MAP,
  };
}
