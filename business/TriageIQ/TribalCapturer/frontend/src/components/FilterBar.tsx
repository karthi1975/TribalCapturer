/**
 * Material-UI Filter Bar Component for Creator Dashboard
 */
import React, { useState } from 'react';
import {
  Paper,
  Stack,
  TextField,
  Button,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

export interface FilterValues {
  facility: string;
  specialty: string;
  searchQuery: string;
}

interface FilterBarProps {
  onFilter: (filters: FilterValues) => void;
  onSearch: (query: string) => void;
  loading?: boolean;
}

const FilterBar: React.FC<FilterBarProps> = ({ onFilter, onSearch, loading = false }) => {
  const [filters, setFilters] = useState<FilterValues>({
    facility: '',
    specialty: '',
    searchQuery: '',
  });

  const handleFilterApply = () => {
    onFilter(filters);
  };

  const handleSearch = () => {
    if (filters.searchQuery.trim()) {
      onSearch(filters.searchQuery.trim());
    }
  };

  const handleClear = () => {
    const clearedFilters = {
      facility: '',
      specialty: '',
      searchQuery: '',
    };
    setFilters(clearedFilters);
    onFilter(clearedFilters);
  };

  const handleKeyPress = (e: React.KeyboardEvent, action: 'filter' | 'search') => {
    if (e.key === 'Enter') {
      if (action === 'filter') {
        handleFilterApply();
      } else {
        handleSearch();
      }
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Stack spacing={2}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            label="Facility"
            placeholder="e.g., St. Mary's Hospital"
            value={filters.facility}
            onChange={(e) => setFilters({ ...filters, facility: e.target.value })}
            onKeyPress={(e) => handleKeyPress(e, 'filter')}
            disabled={loading}
            size="small"
            sx={{ flex: 1 }}
          />

          <TextField
            label="Specialty Service"
            placeholder="e.g., Cardiology"
            value={filters.specialty}
            onChange={(e) => setFilters({ ...filters, specialty: e.target.value })}
            onKeyPress={(e) => handleKeyPress(e, 'filter')}
            disabled={loading}
            size="small"
            sx={{ flex: 1 }}
          />

          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={handleFilterApply}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            Filter
          </Button>

          <Button
            variant="outlined"
            color="secondary"
            startIcon={<ClearIcon />}
            onClick={handleClear}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            Clear
          </Button>
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            fullWidth
            label="Search Knowledge"
            placeholder="Search in knowledge descriptions..."
            value={filters.searchQuery}
            onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
            onKeyPress={(e) => handleKeyPress(e, 'search')}
            disabled={loading}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          <Button
            variant="contained"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={loading || !filters.searchQuery.trim()}
            sx={{ minWidth: 120 }}
          >
            Search
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
};

export default FilterBar;
