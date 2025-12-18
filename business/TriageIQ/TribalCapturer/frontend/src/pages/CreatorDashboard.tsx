/**
 * Creator Dashboard Page
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import AppNavBar from '../components/AppNavBar';
import FilterBar, { FilterValues } from '../components/FilterBar';
import KnowledgeList from '../components/KnowledgeList';
import KnowledgeDetail from '../components/KnowledgeDetail';
import IntelligentSearch from '../components/IntelligentSearch';
import api from '../services/api';
import {
  User,
  KnowledgeEntry,
  KnowledgeEntryList,
  SearchResults,
} from '../types';

interface CreatorDashboardProps {
  user: User;
  onLogout: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const CreatorDashboard: React.FC<CreatorDashboardProps> = ({ user, onLogout }) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [allEntries, setAllEntries] = useState<KnowledgeEntryList | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState<FilterValues>({
    facility: '',
    specialty: '',
    searchQuery: '',
  });

  const fetchAllEntries = async (page: number = 1, filterValues?: FilterValues) => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { page, page_size: 20 };
      if (filterValues?.facility) params.facility = filterValues.facility;
      if (filterValues?.specialty) params.specialty = filterValues.specialty;

      const response = await api.get('/api/v1/knowledge-entries/', { params });
      setAllEntries(response.data);
      setSearchResults(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load entries');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string, page: number = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/v1/knowledge-entries/search/', {
        params: { q: query, page, page_size: 20 },
      });
      setSearchResults(response.data);
      setAllEntries(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentTab === 0) {
      fetchAllEntries(currentPage, filters);
    }
  }, [currentTab, currentPage]);

  const handleFilter = (filterValues: FilterValues) => {
    setFilters(filterValues);
    setCurrentPage(1);
    fetchAllEntries(1, filterValues);
  };

  const handleSearchSubmit = (query: string) => {
    setCurrentPage(1);
    handleSearch(query, 1);
  };

  const handleViewEntry = async (entryId: string) => {
    try {
      const response = await api.get(`/api/v1/knowledge-entries/${entryId}`);
      setSelectedEntry(response.data);
      setDetailOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load entry details');
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    if (searchResults) {
      handleSearch(filters.searchQuery, page);
    } else {
      fetchAllEntries(page, filters);
    }
  };

  // Convert search results to entry summary format for KnowledgeList
  const getDisplayEntries = () => {
    if (searchResults) {
      return searchResults.results.map((result) => ({
        id: result.id,
        ma_name: result.ma_name,
        facility: result.facility,
        specialty_service: result.specialty_service,
        status: 'published' as const,
        created_at: result.created_at,
      }));
    }
    return allEntries?.entries || [];
  };

  const getDisplayPagination = () => {
    return searchResults?.pagination || allEntries?.pagination;
  };

  return (
    <>
      <AppNavBar user={user} onLogout={onLogout} />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom color="primary">
            Creator Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome, {user.full_name}! Browse and search tribal knowledge from Medical Assistants.
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
            <Tab label="📋 Browse All" />
            <Tab label="🧠 Intelligent Search" />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <FilterBar onFilter={handleFilter} onSearch={handleSearchSubmit} loading={loading} />

          {searchResults && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Found {searchResults.pagination.total_items} result(s) for "{filters.searchQuery}"
            </Alert>
          )}

          <KnowledgeList
            entries={getDisplayEntries()}
            pagination={getDisplayPagination()}
            onView={handleViewEntry}
            onPageChange={handlePageChange}
            loading={loading}
            showActions={false}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <IntelligentSearch onResultClick={handleViewEntry} />
        </TabPanel>

        <KnowledgeDetail
          entry={selectedEntry}
          open={detailOpen}
          onClose={() => setDetailOpen(false)}
        />
      </Container>
    </>
  );
};

export default CreatorDashboard;
