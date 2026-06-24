<<<<<<< HEAD
import { ApiResponse } from "@/types/api";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://sid385-fill-the-frames.hf.space/api/v1";

=======
// src/lib/api-client.ts

import { ApiResponse } from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://sid385-fill-the-frames.hf.space/api/v1";

// 🚨 BHAIIII! Dhyan se dekho, yahan 'export' zaroori hai!
>>>>>>> 386dd7c (done with interpolation will add some consistency in future)
export const apiClient = {
  uploadFile: async (file: File): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/upload/`, {
      method: "POST",
<<<<<<< HEAD
      // Agar space private hai toh uncomment karo:
      // headers: { "Authorization": `Bearer ${process.env.NEXT_PUBLIC_HF_TOKEN}` },
=======
>>>>>>> 386dd7c (done with interpolation will add some consistency in future)
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    return response.json();
  },
<<<<<<< HEAD
};
=======
  // src/lib/api-client.ts me apiClient ke andar add karo:

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

// src/lib/api-client.ts me apiClient ke andar add karo:

>>>>>>> 386dd7c (done with interpolation will add some consistency in future)
