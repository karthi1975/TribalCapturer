/**
 * API client for making requests to the backend.
 */
import axios from 'axios';
import type {
  FacilityListResponse,
  FacilityWithCounts,
  FacilityCreateRequest,
  FacilityUpdateRequest,
  Facility,
  SpecialtyListResponse,
  SpecialtyWithCounts,
  SpecialtyCreateRequest,
  SpecialtyUpdateRequest,
  Specialty,
  UserListResponse,
  UserDetailWithAssignments,
  UserCreateRequest,
  UserUpdateRequest,
  UserPasswordResetRequest,
  UserAssignmentsRequest,
  UserAssignmentResponse,
  UserRole
} from '../types';

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

// ============================================================================
// Facility Management APIs
// ============================================================================

export const getFacilities = async (
  page: number = 1,
  pageSize: number = 50,
  activeOnly: boolean = true
): Promise<FacilityListResponse> => {
  const response = await api.get('/api/v1/facilities/', {
    params: { page, page_size: pageSize, active_only: activeOnly }
  });
  return response.data;
};

export const getFacility = async (facilityId: string): Promise<FacilityWithCounts> => {
  const response = await api.get(`/api/v1/facilities/${facilityId}`);
  return response.data;
};

export const createFacility = async (data: FacilityCreateRequest): Promise<Facility> => {
  const response = await api.post('/api/v1/facilities/', data);
  return response.data;
};

export const updateFacility = async (
  facilityId: string,
  data: FacilityUpdateRequest
): Promise<Facility> => {
  const response = await api.put(`/api/v1/facilities/${facilityId}`, data);
  return response.data;
};

export const deactivateFacility = async (facilityId: string): Promise<void> => {
  await api.delete(`/api/v1/facilities/${facilityId}`);
};

export const getMyFacilities = async (): Promise<Facility[]> => {
  const response = await api.get('/api/v1/facilities/my-facilities');
  return response.data;
};

// ============================================================================
// Specialty Management APIs
// ============================================================================

export const getSpecialties = async (
  page: number = 1,
  pageSize: number = 50,
  activeOnly: boolean = true
): Promise<SpecialtyListResponse> => {
  const response = await api.get('/api/v1/specialties/', {
    params: { page, page_size: pageSize, active_only: activeOnly }
  });
  return response.data;
};

export const getSpecialty = async (specialtyId: string): Promise<SpecialtyWithCounts> => {
  const response = await api.get(`/api/v1/specialties/${specialtyId}`);
  return response.data;
};

export const createSpecialty = async (data: SpecialtyCreateRequest): Promise<Specialty> => {
  const response = await api.post('/api/v1/specialties/', data);
  return response.data;
};

export const updateSpecialty = async (
  specialtyId: string,
  data: SpecialtyUpdateRequest
): Promise<Specialty> => {
  const response = await api.put(`/api/v1/specialties/${specialtyId}`, data);
  return response.data;
};

export const deactivateSpecialty = async (specialtyId: string): Promise<void> => {
  await api.delete(`/api/v1/specialties/${specialtyId}`);
};

export const getMySpecialties = async (): Promise<Specialty[]> => {
  const response = await api.get('/api/v1/specialties/my-specialties');
  return response.data;
};

// ============================================================================
// User Management APIs
// ============================================================================

export const getUsers = async (
  page: number = 1,
  pageSize: number = 20,
  role?: UserRole,
  activeOnly: boolean = true
): Promise<UserListResponse> => {
  const response = await api.get('/api/v1/user-management/users', {
    params: { page, page_size: pageSize, role, active_only: activeOnly }
  });
  return response.data;
};

export const getUser = async (userId: string): Promise<UserDetailWithAssignments> => {
  const response = await api.get(`/api/v1/user-management/users/${userId}`);
  return response.data;
};

export const createUser = async (data: UserCreateRequest): Promise<UserDetailWithAssignments> => {
  const response = await api.post('/api/v1/user-management/users', data);
  return response.data;
};

export const updateUser = async (
  userId: string,
  data: UserUpdateRequest
): Promise<UserDetailWithAssignments> => {
  const response = await api.put(`/api/v1/user-management/users/${userId}`, data);
  return response.data;
};

export const activateUser = async (userId: string): Promise<void> => {
  await api.post(`/api/v1/user-management/users/${userId}/activate`);
};

export const deactivateUser = async (userId: string): Promise<void> => {
  await api.post(`/api/v1/user-management/users/${userId}/deactivate`);
};

export const resetUserPassword = async (
  userId: string,
  data: UserPasswordResetRequest
): Promise<void> => {
  await api.post(`/api/v1/user-management/users/${userId}/reset-password`, data);
};

export const updateUserAssignments = async (
  userId: string,
  data: UserAssignmentsRequest
): Promise<void> => {
  await api.put(`/api/v1/user-management/users/${userId}/assignments`, data);
};

export const getUserAssignments = async (userId: string): Promise<UserAssignmentResponse> => {
  const response = await api.get(`/api/v1/user-management/users/${userId}/assignments`);
  return response.data;
};

export default api;
