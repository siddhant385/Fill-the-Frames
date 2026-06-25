import { api, ApiResponse } from "./base-client";

export const metadataClient = {
  getMetadata: (fileId: string): Promise<ApiResponse> => {
    return api.get<ApiResponse>(`/metadata/${fileId}`);
  },
};
