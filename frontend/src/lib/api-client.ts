import { ApiResponse } from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://sid385-fill-the-frames.hf.space/api/v1";

export const apiClient = {
  uploadFile: async (file: File): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/upload/`, {
      method: "POST",
      // Agar space private hai toh uncomment karo:
      // headers: { "Authorization": `Bearer ${process.env.NEXT_PUBLIC_HF_TOKEN}` },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    return response.json();
  },

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
};
