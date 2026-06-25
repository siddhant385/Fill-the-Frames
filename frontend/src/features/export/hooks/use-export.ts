import { useState, useCallback } from "react";
import { ExportJob, ExportOptions } from "../types";
import { DEFAULT_EXPORT_OPTIONS } from "../constants";
import { exportClient } from "@/lib/api";
import { useUploadStore } from "@/store/upload-store";

export function useExport() {
  const [options, setOptions] = useState<ExportOptions>(DEFAULT_EXPORT_OPTIONS);
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const files = useUploadStore(state => state.files);

  const startExport = useCallback(() => {
    // Select the latest completed file
    const completedFiles = files.filter(f => f.status === 'completed' && f.cloudFileId);
    if (completedFiles.length === 0) {
      alert("No files available for export. Please upload a file first.");
      return;
    }
    
    const targetFile = completedFiles[completedFiles.length - 1]; // latest
    const newJobId = `job-${Date.now()}`;
    
    const downloadUrl = exportClient.getDownloadUrl(targetFile.cloudFileId!);

    const newJob: ExportJob = {
      id: newJobId,
      format: options.format,
      status: "completed", // Backend provides direct download link currently
      progress: 100,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      downloadUrl: downloadUrl,
      fileSize: `${((targetFile.fileInfo?.size || 0) / (1024*1024)).toFixed(2)} MB`
    };

    setJobs((prev) => [newJob, ...prev]);

    // Open download directly
    window.open(downloadUrl, "_blank");
  }, [options, files]);

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