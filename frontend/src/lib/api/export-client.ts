import { BASE_URL } from "./base-client";

export const exportClient = {
  getDownloadUrl: (fileId: string): string =>
    `${BASE_URL}/export/download/${fileId}`,
};
