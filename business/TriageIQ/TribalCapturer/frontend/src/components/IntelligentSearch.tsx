/**
 * Intelligent Semantic Search Component with Relevance Scores
 */
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Chip,
  Stack,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Psychology as AIIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import api from '../services/api';
import { KnowledgeType } from '../types';

interface SearchResult {
  entry: {
    id: string;
    ma_name: string;
    facility: string;
    specialty_service: string;
    provider_name?: string;
    knowledge_type: string;
    is_continuity_care: boolean;
    knowledge_description: string;
    created_at: string;
  };
  relevance_score: number;
  match_type: 'semantic' | 'keyword';
}

interface IntelligentSearchProps {
  onResultClick?: (entryId: string) => void;
}

const IntelligentSearch: React.FC<IntelligentSearchProps> = ({ onResultClick }) => {
  const [query, setQuery] = useState('');
  const [facility, setFacility] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [provider, setProvider] = useState('');
  const [knowledgeType, setKnowledgeType] = useState('');
  const [continuityOnly, setContinuityOnly] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    const startTime = Date.now();

    try {
      const params: any = { q: query, top_k: 10 };
      if (facility) params.facility = facility;
      if (specialty) params.specialty = specialty;
      if (provider) params.provider = provider;
      if (knowledgeType) params.knowledge_type = knowledgeType;
      if (continuityOnly) params.continuity_care_only = true;

      const response = await api.get('/api/v1/knowledge-entries/smart-search/', { params });
      setResults(response.data.results);
      setSearchTime(Date.now() - startTime);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score > 0.8) return 'success';
    if (score > 0.6) return 'primary';
    if (score > 0.4) return 'warning';
    return 'default';
  };

  return (
    <Box>
      <Stack spacing={2}>
        {/* Search Input */}
        <TextField
          fullWidth
          label="🧠 Intelligent Search"
          placeholder="e.g., Crohn's disease scheduling, heart failure follow-up requirements"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          InputProps={{
            endAdornment: (
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                disabled={loading || !query.trim()}
              >
                Search
              </Button>
            ),
          }}
          helperText="Uses AI to understand context, not just keywords. Auto-falls back to keyword search if needed."
        />

        {/* Filters */}
        <Stack direction="row" spacing={2} flexWrap="wrap">
          <TextField
            label="Facility"
            value={facility}
            onChange={(e) => setFacility(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          />
          <TextField
            label="Specialty"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          />
          <TextField
            label="Provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          />
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Knowledge Type</InputLabel>
            <Select
              value={knowledgeType}
              label="Knowledge Type"
              onChange={(e) => setKnowledgeType(e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value={KnowledgeType.DIAGNOSIS_SPECIALTY}>Diagnosis → Specialty</MenuItem>
              <MenuItem value={KnowledgeType.PROVIDER_PREFERENCE}>Provider Preference</MenuItem>
              <MenuItem value={KnowledgeType.CONTINUITY_CARE}>Continuity of Care</MenuItem>
              <MenuItem value={KnowledgeType.PRE_VISIT_REQUIREMENT}>Pre-Visit Requirement</MenuItem>
              <MenuItem value={KnowledgeType.SCHEDULING_WORKFLOW}>Scheduling Workflow</MenuItem>
              <MenuItem value={KnowledgeType.GENERAL_KNOWLEDGE}>General Knowledge</MenuItem>
            </Select>
          </FormControl>
          <FormControlLabel
            control={
              <Checkbox
                checked={continuityOnly}
                onChange={(e) => setContinuityOnly(e.target.checked)}
              />
            }
            label="Continuity of Care Only"
          />
        </Stack>

        {/* Search Status */}
        {loading && <LinearProgress />}

        {error && <Alert severity="error">{error}</Alert>}

        {searchTime !== null && !loading && (
          <Alert severity="info" icon={<SpeedIcon />}>
            Found {results.length} results in {searchTime}ms
            {results.some((r) => r.match_type === 'semantic') && (
              <Chip
                icon={<AIIcon />}
                label="AI-Powered"
                size="small"
                color="primary"
                sx={{ ml: 1 }}
              />
            )}
          </Alert>
        )}

        {/* Results */}
        <Stack spacing={2}>
          {results.map((result, index) => (
            <Card
              key={result.entry.id}
              variant="outlined"
              sx={{
                cursor: 'pointer',
                '&:hover': { boxShadow: 3 },
                borderLeft: 4,
                borderLeftColor:
                  result.relevance_score > 0.8
                    ? 'success.main'
                    : result.relevance_score > 0.6
                    ? 'primary.main'
                    : 'warning.main',
              }}
              onClick={() => onResultClick?.(result.entry.id)}
            >
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="start">
                  <Box flex={1}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <Typography variant="h6">{result.entry.specialty_service}</Typography>
                      {result.entry.provider_name && (
                        <Chip label={result.entry.provider_name} size="small" />
                      )}
                      {result.entry.is_continuity_care && (
                        <Chip label="Continuity of Care" size="small" color="primary" />
                      )}
                    </Stack>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      📍 {result.entry.facility} • 👤 {result.entry.ma_name}
                    </Typography>

                    <Typography variant="body1" paragraph>
                      {result.entry.knowledge_description.length > 200
                        ? result.entry.knowledge_description.substring(0, 200) + '...'
                        : result.entry.knowledge_description}
                    </Typography>

                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={result.entry.knowledge_type.replace('_', ' ').toUpperCase()}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={result.match_type === 'semantic' ? '🧠 AI Match' : '🔍 Keyword Match'}
                        size="small"
                        color={result.match_type === 'semantic' ? 'primary' : 'default'}
                      />
                    </Stack>
                  </Box>

                  <Tooltip title={`Relevance: ${(result.relevance_score * 100).toFixed(0)}%`}>
                    <Chip
                      label={`${(result.relevance_score * 100).toFixed(0)}%`}
                      color={getRelevanceColor(result.relevance_score)}
                      sx={{ ml: 2 }}
                    />
                  </Tooltip>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>

        {results.length === 0 && !loading && query && (
          <Alert severity="info">
            No results found. Try different keywords or broaden your filters.
          </Alert>
        )}
      </Stack>
    </Box>
  );
};

export default IntelligentSearch;
