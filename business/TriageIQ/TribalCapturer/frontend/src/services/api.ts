/**
 * API client for making requests to the backend.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8777',
  withCredentials: true, // Important for HTTPOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      const currentPath = window.location.pathname;
      if (currentPath !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Download a single knowledge entry as PDF.
 *
 * @param entryId - UUID of the knowledge entry
 * @throws Error if download fails
 */
export const downloadSingleEntryPDF = async (entryId: string): Promise<void> => {
  const response = await api.get(`/api/v1/knowledge-entries/${entryId}/export-pdf`, {
    responseType: 'blob',
  });

  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `knowledge_entry_${entryId}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Download multiple knowledge entries as a single PDF (one per page).
 *
 * @param entryIds - Array of entry UUIDs
 * @throws Error if download fails or too many entries
 */
export const downloadBulkEntriesPDF = async (entryIds: string[]): Promise<void> => {
  const response = await api.post(
    '/api/v1/knowledge-entries/export-pdf-bulk',
    { entry_ids: entryIds },
    { responseType: 'blob' }
  );

  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  const timestamp = new Date().toISOString().split('T')[0];
  link.download = `knowledge_entries_${timestamp}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api;
