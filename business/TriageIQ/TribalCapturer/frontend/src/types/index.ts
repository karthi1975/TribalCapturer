/**
 * TypeScript type definitions for the Tribal Knowledge Capture Portal.
 */

export enum UserRole {
  MA = 'MA',
  CREATOR = 'Creator'
}

export enum EntryStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published'
}

export enum KnowledgeType {
  DIAGNOSIS_SPECIALTY = 'diagnosis_specialty',
  PROVIDER_PREFERENCE = 'provider_preference',
  CONTINUITY_CARE = 'continuity_care',
  PRE_VISIT_REQUIREMENT = 'pre_visit_requirement',
  SCHEDULING_WORKFLOW = 'scheduling_workflow',
  GENERAL_KNOWLEDGE = 'general_knowledge'
}

export interface User {
  id: string;
  username: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface KnowledgeEntry {
  id: string;
  user_id: string;
  ma_name: string;
  facility: string;
  specialty_service: string;
  provider_name?: string;
  knowledge_type: KnowledgeType;
  is_continuity_care: boolean;
  knowledge_description: string;
  status: EntryStatus;
  created_at: string;
  updated_at?: string;
}

export interface KnowledgeEntrySummary {
  id: string;
  ma_name: string;
  facility: string;
  specialty_service: string;
  provider_name?: string;
  knowledge_type: KnowledgeType;
  is_continuity_care: boolean;
  status: EntryStatus;
  created_at: string;
  updated_at?: string;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface KnowledgeEntryList {
  entries: KnowledgeEntrySummary[];
  pagination: Pagination;
}

export interface SearchResult {
  id: string;
  ma_name: string;
  facility: string;
  specialty_service: string;
  knowledge_type: KnowledgeType;
  is_continuity_care: boolean;
  created_at: string;
  highlighted_snippet: string;
}

export interface SearchResults {
  results: SearchResult[];
  pagination: Pagination;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  message: string;
}

export interface KnowledgeEntryCreateRequest {
  facility: string;
  specialty_service: string;
  provider_name?: string;
  knowledge_type?: KnowledgeType;
  is_continuity_care?: boolean;
  knowledge_description: string;
  status?: EntryStatus;
}

export interface KnowledgeEntryUpdateRequest {
  facility?: string;
  specialty_service?: string;
  provider_name?: string;
  knowledge_type?: KnowledgeType;
  is_continuity_care?: boolean;
  knowledge_description?: string;
  status?: EntryStatus;
}

export interface ApiError {
  detail: string;
}

export interface BatchKnowledgeEntryRequest {
  entries: KnowledgeEntryCreateRequest[];
}

export interface BatchKnowledgeEntryResponse {
  total_submitted: number;
  total_created: number;
  entries: KnowledgeEntry[];
  message: string;
}

// New types for user management and facility/specialty management

export interface Facility {
  id: string;
  name: string;
  code?: string;
  is_active: boolean;
  created_at: string;
}

export interface FacilityWithCounts extends Facility {
  assigned_user_count: number;
  knowledge_entry_count: number;
}

export interface FacilityListResponse {
  facilities: Facility[];
  total: number;
  page: number;
  page_size: number;
}

export interface Specialty {
  id: string;
  name: string;
  code?: string;
  is_active: boolean;
  created_at: string;
}

export interface SpecialtyWithCounts extends Specialty {
  assigned_user_count: number;
  knowledge_entry_count: number;
}

export interface SpecialtyListResponse {
  specialties: Specialty[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserDetailWithAssignments extends User {
  assigned_facilities: Facility[];
  assigned_specialties: Specialty[];
}

export interface UserListResponse {
  users: UserDetailWithAssignments[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserCreateRequest {
  username: string;
  password: string;
  full_name: string;
  role: UserRole;
  facility_ids?: string[];
  specialty_ids?: string[];
}

export interface UserUpdateRequest {
  full_name?: string;
  is_active?: boolean;
}

export interface UserPasswordResetRequest {
  new_password: string;
}

export interface UserAssignmentsRequest {
  facility_ids: string[];
  specialty_ids: string[];
}

export interface UserAssignmentResponse {
  facilities: Facility[];
  specialties: Specialty[];
}

export interface FacilityCreateRequest {
  name: string;
  code?: string;
}

export interface FacilityUpdateRequest {
  name?: string;
  code?: string;
  is_active?: boolean;
}

export interface SpecialtyCreateRequest {
  name: string;
  code?: string;
}

export interface SpecialtyUpdateRequest {
  name?: string;
  code?: string;
  is_active?: boolean;
}
