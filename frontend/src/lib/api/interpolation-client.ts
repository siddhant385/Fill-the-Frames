import { ApiResponse } from "@/types/api";
import { BASE_URL } from "./base-client";

export const interpolationClient = {
  generateInterpolation: async (fileId1: string, fileId2: string, variable: string = "C13"): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append("file_id_1", fileId1);
    formData.append("file_id_2", fileId2);
    formData.append("variable", variable);

    const response = await fetch(`${BASE_URL}/interpolation/generate`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Generation failed with status ${response.status}`);
    }

    return response.json();
  },

  getJobStatus: async (jobId: string): Promise<ApiResponse> => {
    const response = await fetch(`${BASE_URL}/interpolation/status/${jobId}`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch job status with status ${response.status}`);
    }

    return response.json();
  }
};
