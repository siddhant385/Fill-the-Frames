import { api, ApiResponse } from "./base-client";

export interface AnimationSequenceResponse {
  file_id: string;
  frames: unknown[];
  fps: number;
}

export const animationClient = {
  getSequence: (
    fileId: string,
    params?: { start_time?: string; end_time?: string; fps?: number }
  ): Promise<ApiResponse<AnimationSequenceResponse>> =>
    api.get(`/animation/${fileId}/sequence`, { params }),
};
