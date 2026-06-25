import { api, ApiResponse } from "./base-client";

export interface MetricsResponse extends ApiResponse {
  data: {
    mse?: number;
    psnr?: number;
    ssim?: number;
    [key: string]: any;
  };
}

export const validationClient = {
  validate: (fileId: string): Promise<MetricsResponse> => {
    return api.post<MetricsResponse>("/validation/run", { fileId });
  }
};
