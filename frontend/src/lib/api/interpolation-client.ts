import { api, ApiResponse } from "./base-client";

export const interpolationClient = {
  generate: (fileId1: string, fileId2: string, variable: string = "C13"): Promise<ApiResponse> => {
    // API endpoint expects POST with form data? Wait, interpolation.py might expect JSON or query params.
    // Let's use JSON if it's a typical endpoint, but earlier code used FormData. We'll use JSON if backend accepts it, but to be safe let's use what api-client.ts had.
    // The previous `api-client.ts` used FormData.
    const formData = new FormData();
    formData.append("file_id_1", fileId1);
    formData.append("file_id_2", fileId2);
    formData.append("variable", variable);
    
    // Oh wait, `interpolationClient.generate` was using form data. Let's use `postFormData`.
    return api.postFormData<ApiResponse>("/interpolation/generate", formData);
  },

  getStatus: (jobId: string): Promise<ApiResponse> => {
    return api.get<ApiResponse>(`/interpolation/status/${jobId}`);
  },

  // Note: events might return Server-Sent Events (SSE) which is not standard JSON
  getEventsUrl: (jobId: string): string => {
    return `/interpolation/events/${jobId}`;
  }
};
