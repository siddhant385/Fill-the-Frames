import { api, ApiResponse } from "./base-client";

export const visualizationClient = {
  getVariables: (fileId: string): Promise<ApiResponse> => {
    return api.get<ApiResponse>(`/visualization/${fileId}/variables`);
  },

  getBounds: (fileId: string): Promise<ApiResponse> => {
    return api.get<ApiResponse>(`/visualization/${fileId}/bounds`);
  },

  // Note: These endpoints might return images/tiles rather than JSON
  getLayerUrl: (fileId: string, variable: string, timestamp: number): string => {
    return `/visualization/${fileId}/layer?variable=${variable}&timestamp=${timestamp}`;
  },

  getErrorMapLayerUrl: (fileId1: string, fileId2: string, variable: string, timestamp: number): string => {
    return `/visualization/error-map/layer?file_id_1=${fileId1}&file_id_2=${fileId2}&variable=${variable}&timestamp=${timestamp}`;
  }
};
