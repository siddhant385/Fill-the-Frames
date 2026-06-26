import { BASE_URL, ApiResponse, ApiError } from './base-client';

export interface GpuStatusResponse {
  cuda_available: boolean;
}

export interface ModelsStatusResponse {
  rife: string;
}

const ROOT_URL = BASE_URL.replace(/\/api\/v1\/?$/, '');

async function fetchHealth<T>(path: string): Promise<T> {
  const response = await fetch(`${ROOT_URL}${path}`);
  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}`, response.status);
  }
  const result = await response.json() as ApiResponse<T>;
  return result.data;
}

export const healthClient = {
  getGpuStatus: async (): Promise<GpuStatusResponse> => {
    return fetchHealth<GpuStatusResponse>('/gpu');
  },
  
  getModelsStatus: async (): Promise<ModelsStatusResponse> => {
    return fetchHealth<ModelsStatusResponse>('/models');
  }
};
