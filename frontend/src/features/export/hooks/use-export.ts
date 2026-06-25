import { useState, useCallback } from "react";
import { ExportJob, ExportOptions } from "../types";
import { DEFAULT_EXPORT_OPTIONS } from "../constants";
import { exportClient } from "@/lib/api/export-client";
import { useInterpolationStore } from "@/store/interpolation-store";

export function useExport() {
  const [options, setOptions] = useState<ExportOptions>(DEFAULT_EXPORT_OPTIONS);
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const interpolationStore = useInterpolationStore();

  const startExport = useCallback(() => {
    const targetFileId = interpolationStore.outputFileId;
    if (!targetFileId) {
      alert("No generated file available for export. Please run interpolation first.");
      return;
    }
    
    const newJobId = `job-${Date.now()}`;
    const downloadUrl = exportClient.getDownloadUrl(targetFileId);

    const newJob: ExportJob = {
      id: newJobId,
      format: options.format,
      status: "completed",
      progress: 100,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      downloadUrl: downloadUrl,
      fileSize: "Unknown" // Can't know size until downloaded
    };

    setJobs((prev) => [newJob, ...prev]);

    // Open download directly
    window.open(downloadUrl, "_blank");
  }, [options, interpolationStore.outputFileId]);

  const cancelExport = useCallback((jobId: string) => {
    // Not applicable since it's instant
  }, []);

  const updateOptions = useCallback((newOptions: Partial<ExportOptions>) => {
    setOptions((prev) => ({ ...prev, ...newOptions }));
  }, []);

  const activeJobs = jobs.filter((j) => j.status === "preparing" || j.status === "exporting");
  const historyJobs = jobs.filter((j) => j.status === "completed" || j.status === "error");

  const stats = {
    total: jobs.length,
    successful: jobs.filter(j => j.status === "completed").length,
    failed: jobs.filter(j => j.status === "error").length,
    queueLength: activeJobs.length,
  };

  return {
    options,
    jobs,
    activeJobs,
    historyJobs,
    stats,
    startExport,
    cancelExport,
    updateOptions,
  };
}