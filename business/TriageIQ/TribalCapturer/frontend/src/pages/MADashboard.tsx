/**
 * Medical Assistant Dashboard Page
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import AppNavBar from '../components/AppNavBar';
import KnowledgeEntryForm from '../components/KnowledgeEntryForm';
import KnowledgeList from '../components/KnowledgeList';
import KnowledgeDetail from '../components/KnowledgeDetail';
import api from '../services/api';
import {
  User,
  KnowledgeEntryCreateRequest,
  KnowledgeEntry,
  KnowledgeEntryList,
} from '../types';

interface MADashboardProps {
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

const MADashboard: React.FC<MADashboardProps> = ({ user, onLogout }) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [myEntries, setMyEntries] = useState<KnowledgeEntryList | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchMyEntries = async (page: number = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/v1/knowledge-entries/my-entries', {
        params: { page, page_size: 20 },
      });
      setMyEntries(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load entries');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentTab === 1) {
      fetchMyEntries(currentPage);
    }
  }, [currentTab, currentPage]);

  const handleSubmit = async (data: KnowledgeEntryCreateRequest, isDraft: boolean) => {
    try {
      await api.post('/api/v1/knowledge-entries/', data);
      // Refresh entries if on My Entries tab
      if (currentTab === 1) {
        fetchMyEntries(currentPage);
      }
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create entry');
    }
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
  };

  return (
    <>
      <AppNavBar user={user} onLogout={onLogout} />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom color="primary">
            Medical Assistant Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome, {user.full_name}! Capture and manage your tribal knowledge.
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
            <Tab label="Submit Knowledge" />
            <Tab label="My Entries" />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <KnowledgeEntryForm onSubmit={handleSubmit} />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          {myEntries && (
            <KnowledgeList
              entries={myEntries.entries}
              pagination={myEntries.pagination}
              onView={handleViewEntry}
              onPageChange={handlePageChange}
              loading={loading}
              showActions={false}
            />
          )}
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

export default MADashboard;
