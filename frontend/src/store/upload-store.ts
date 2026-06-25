import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { validateSatelliteFile } from '@/features/upload/utils/file-validation';
import { uploadClient } from '@/lib/api';

export type UploadStatus = 'pending' | 'validating' | 'ready' | 'uploading' | 'completed' | 'error';

// A surrogate for File metadata so we can persist it
export interface PersistedFileInfo {
  name: string;
  size: number;
}

export interface UploadFile {
  id: string;
  file?: File; // Optional because persisted files won't have the actual File object
  fileInfo: PersistedFileInfo; // Guaranteed to exist for UI rendering
  progress: number;
  status: UploadStatus;
  error?: string;
  uploadedAt?: Date;
  fileType?: 'netcdf' | 'hdf5';
  cloudFileId?: string;
}

interface UploadStore {
  files: UploadFile[];
  addFiles: (files: File[]) => void;
  removeFile: (id: string) => void;
  uploadFileToServer: (id: string) => Promise<void>;
  startAllReadyUploads: () => void;
  clearCompleted: () => void;
  fetchRemoteFiles: () => Promise<void>;
}

export const useUploadStore = create<UploadStore>()(
  persist(
    (set, get) => ({
      files: [],

      addFiles: (newFiles) => {
        set((state) => {
          const addedFiles: UploadFile[] = newFiles.map((file) => {
            const id = Math.random().toString(36).substring(2, 9);
            const validation = validateSatelliteFile(file);
            
            return {
              id,
              file,
              fileInfo: { name: file.name, size: file.size },
              progress: 0,
              status: validation.isValid ? 'ready' : 'error',
              error: validation.error,
              fileType: validation.fileType,
            };
          });

          return { files: [...state.files, ...addedFiles] };
        });
      },

      removeFile: (id) => {
        set((state) => ({
          files: state.files.filter((f) => f.id !== id),
        }));
      },

      uploadFileToServer: async (id: string) => {
        const fileToUpload = get().files.find(f => f.id === id);
        if (!fileToUpload || fileToUpload.status !== 'ready' || !fileToUpload.file) return;

        set((state) => ({
          files: state.files.map((f) =>
            f.id === id ? { ...f, status: 'uploading', progress: 10 } : f
          ),
        }));

        try {
          const response = await uploadClient.uploadFile(fileToUpload.file);
          
          if (response.success) {
            set((state) => ({
              files: state.files.map((f) =>
                f.id === id ? { 
                  ...f, 
                  progress: 100, 
                  status: 'completed', 
                  uploadedAt: new Date(),
                  cloudFileId: response.data?.fileId || response.data?.file_id || id
                } : f
              ),
            }));
          } else {
            throw new Error(response.message || "Upload failed from server");
          }
        } catch (error: any) {
          set((state) => ({
            files: state.files.map((f) =>
              f.id === id ? { ...f, status: 'error', error: error.message } : f
            ),
          }));
        }
      },

      startAllReadyUploads: () => {
        const { files, uploadFileToServer } = get();
        files.forEach((f) => {
          if (f.status === 'ready') {
            uploadFileToServer(f.id);
          }
        });
      },

      clearCompleted: () => {
        set((state) => ({
          files: state.files.filter((f) => f.status !== 'completed'),
        }));
      },

      fetchRemoteFiles: async () => {
        try {
           const res = await uploadClient.getFiles();
           if (res.success && Array.isArray(res.data)) {
             // Sync backend files into store
             const remoteFiles: UploadFile[] = res.data.map((f: any) => ({
                id: f.id || Math.random().toString(36).substring(2, 9),
                fileInfo: { name: f.filename || f.id, size: f.size || 0 },
                progress: 100,
                status: 'completed',
                cloudFileId: f.id,
                uploadedAt: new Date(f.uploaded_at || Date.now())
             }));

             set((state) => {
                // merge avoiding duplicates by cloudFileId
                const existingIds = new Set(state.files.map(f => f.cloudFileId).filter(Boolean));
                const newFiles = remoteFiles.filter(rf => !existingIds.has(rf.cloudFileId));
                return { files: [...state.files, ...newFiles] };
             });
           }
        } catch (err) {
           console.error("Failed to fetch remote files", err);
        }
      }
    }),
    {
      name: 'satellite-upload-store',
      partialize: (state) => ({
        // Only persist completed files (since we can't persist File objects)
        files: state.files.filter(f => f.status === 'completed').map(f => ({
          ...f,
          file: undefined // Ensure File object is stripped out
        }))
      })
    }
  )
);