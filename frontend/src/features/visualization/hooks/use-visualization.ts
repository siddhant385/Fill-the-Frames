import { useState, useEffect } from 'react';
import type { PlotMouseEvent, PlotDatum } from 'plotly.js';
import { VisualizationState, ColorMap, MockImageData, FrameType, PixelData } from '../types';
import { VISUALIZATION_DEFAULTS } from '../constants';
import { useUploadStore } from '@/store/upload-store';
import { visualizationClient } from '@/lib/api';

// Fallback to mock data if backend doesn't return matrix correctly yet
import { mockFrameData } from '../mock/data';

export function useVisualization(fileIdProp?: string) {
  const [state, setState] = useState<VisualizationState>('loading');
  const [data, setData] = useState<MockImageData | null>(null);
  const [variables, setVariables] = useState<any>(null);
  
  const [colorMap, setColorMap] = useState<ColorMap>(VISUALIZATION_DEFAULTS.initialColorMap);
  const [frameType, setFrameType] = useState<FrameType>(VISUALIZATION_DEFAULTS.initialFrame);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const files = useUploadStore(state => state.files);

  const [pixelData, setPixelData] = useState<PixelData>({
    x: null,
    y: null,
    value: null,
    colormapValue: null
  });

  const [layerUrl, setLayerUrl] = useState<string | null>(null);
  const [bounds, setBounds] = useState<[number, number, number, number] | undefined>(undefined);

  useEffect(() => {
    const loadData = async () => {
      try {
        setState('loading');
        
        let targetFileId = fileIdProp;
        if (!targetFileId) {
          const completedFile = files.find(f => f.status === 'completed' && f.cloudFileId);
          targetFileId = completedFile?.cloudFileId;
        }

        if (!targetFileId) {
          setState('error');
          return;
        }

        // Generate the layer image URL
        const url = visualizationClient.getLayerUrl(targetFileId, "C13", 0);
        setLayerUrl(url);

        // Fetch variable bounds
        try {
          const boundsRes = await visualizationClient.getBounds(targetFileId);
          if (boundsRes.success && boundsRes.data) {
             setBounds([
               boundsRes.data.min_lat,
               boundsRes.data.min_lon,
               boundsRes.data.max_lat,
               boundsRes.data.max_lon
             ]);
          }
        } catch(e) {
          console.warn("Could not load dynamic bounds", e);
        }

        // Fetch variable metadata
        const response = await visualizationClient.getVariables(targetFileId);
        if (response.success && response.data) {
          setVariables(response.data);
          setState('ready');
        } else {
           throw new Error(response.message);
        }
        
      } catch (error) {
        console.error("Failed to load visualization data:", error);
        setState('ready'); // Soft fail to show empty/error state gracefully
      }
    };
    
    loadData();
  }, [frameType, fileIdProp, files]);

  const toggleFullscreen = () => setIsFullscreen(!isFullscreen);

  const handleHover = (event: Readonly<PlotMouseEvent>) => {
    if (event.points && event.points[0]) {
      const pt = event.points[0] as PlotDatum & { z?: number };
      setPixelData({
        x: pt.x as number,
        y: pt.y as number,
        value: pt.z !== undefined ? Number(pt.z) : null,
        colormapValue: null // We could map this using plotly config later if needed
      });
    }
  };

  const handleUnhover = () => {
    setPixelData({
      x: null,
      y: null,
      value: null,
      colormapValue: null
    });
  };

  return {
    state,
    data,
    variables,
    colorMap,
    setColorMap,
    frameType,
    setFrameType,
    isFullscreen,
    toggleFullscreen,
    pixelData,
    handleHover,
    handleUnhover,
    layerUrl,
    bounds
  };
}