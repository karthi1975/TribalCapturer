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
