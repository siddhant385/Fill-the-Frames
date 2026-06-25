import { api, ApiResponse } from "./base-client";

export const uploadClient = {
  uploadFile: (file: File): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return api.postFormData<ApiResponse>("/upload/", formData);
  },

  uploadBatch: (files: File[]): Promise<ApiResponse> => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return api.postFormData<ApiResponse>("/upload/batch", formData);
  },

  getFiles: (): Promise<ApiResponse> => {
    return api.get<ApiResponse>("/upload/");
  },

  deleteFile: (fileId: string): Promise<ApiResponse> => {
    return api.delete<ApiResponse>(`/upload/${fileId}`);
  },
};
