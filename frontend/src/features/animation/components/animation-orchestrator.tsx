"use client";

import { useEffect, useState, useRef } from "react";
import { useInterpolationStore } from "@/store/interpolation-store";
import { useAnimationStore } from "@/store/animation-store";
import { visualizationClient } from "@/lib/api/visualization-client";
import { AnimationFrame } from "@/features/animation/types";

// Helper to preload image and check if it exists
const preloadImage = (src: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = src;
  });
};

export function AnimationOrchestrator() {
  const { t0FileId, t1FileId, outputFileId, t0Metadata, t1Metadata } = useInterpolationStore();
  const { setFrames, setLoading, setError, selectedVariable, cachedBounds, setCachedBounds } = useAnimationStore();
  const [orchestrated, setOrchestrated] = useState(false);
  const prevVariable = useRef(selectedVariable);

  useEffect(() => {
    const variableChanged = prevVariable.current !== selectedVariable;
    prevVariable.current = selectedVariable;

    // We only orchestrate if we have the workflow file IDs
    if (!t0FileId || !t1FileId) {
      setFrames([]);
      setOrchestrated(true);
      return;
    }

    const varToFetch = selectedVariable || "C13";
    const cacheBuster = Date.now(); // Prevents stale browser cache if data regenerated

    const fetchSequence = async () => {
      setLoading(true);
      setError(null);

      try {
        let boundsData = cachedBounds[t0FileId];
        
        // Only fetch bounds if we don't have them cached for this dataset
        if (!boundsData) {
          const boundsRes = await visualizationClient.getBounds(t0FileId, varToFetch);
          if (boundsRes.data?.bounds) {
            boundsData = boundsRes.data.bounds as any;
            setCachedBounds(t0FileId, boundsData as any);
          }
        }

        const parseTimestamp = (metadata: any, defaultStr: string) => {
          if (!metadata?.attributes) return defaultStr;
          const ts = metadata.attributes.time_coverage_start || metadata.attributes.start_date;
          return ts ? ts.toString() : defaultStr;
        };

        const t0Time = parseTimestamp(t0Metadata, "T0 (Past)");
        const t1Time = parseTimestamp(t1Metadata, "T1 (Future)");
        const t05Time = "T0.5 (Interpolated)"; 

        const rawSequence = [
          {
            frameId: t0FileId,
            timestamp: t0Time,
            imageUrl: `${visualizationClient.getLayerUrl(t0FileId, varToFetch)}&v=${cacheBuster}`,
            bounds: boundsData,
            variable: varToFetch
          },
          ...(outputFileId ? [{
            frameId: outputFileId,
            timestamp: t05Time,
            imageUrl: `${visualizationClient.getLayerUrl(outputFileId, varToFetch)}&v=${cacheBuster}`,
            bounds: boundsData,
            variable: varToFetch
          }] : []),
          {
            frameId: t1FileId,
            timestamp: t1Time,
            imageUrl: `${visualizationClient.getLayerUrl(t1FileId, varToFetch)}&v=${cacheBuster}`,
            bounds: boundsData,
            variable: varToFetch
          }
        ];

        // Preload all and filter out failed layers
        const verifiedSequence: AnimationFrame[] = [];
        
        for (const frame of rawSequence) {
          const success = await preloadImage(frame.imageUrl);
          if (success) {
            verifiedSequence.push(frame);
          } else {
            console.warn(`[Animation] Failed to load layer for frame ${frame.frameId}, skipping.`);
          }
        }

        if (verifiedSequence.length === 0) {
          throw new Error("All visualization layers failed to load for this variable.");
        }

        setFrames(verifiedSequence);
      } catch (err: any) {
        console.error("Failed to orchestrate animation:", err);
        setError(err.message || "Failed to load animation sequence");
        // Keep existing frames if variable switch failed, or clear if first load
        if (!variableChanged) setFrames([]);
      } finally {
        setLoading(false);
        setOrchestrated(true);
      }
    };

    fetchSequence();
  }, [t0FileId, t1FileId, outputFileId, t0Metadata, t1Metadata, selectedVariable, setFrames, setLoading, setError, cachedBounds, setCachedBounds]);

  return null;
}
