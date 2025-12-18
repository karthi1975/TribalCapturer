/**
 * Material-UI Knowledge List Component
 */
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Pagination,
  CircularProgress,
  Checkbox,
  Button,
  Alert,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PictureAsPdf as PdfIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { KnowledgeEntrySummary, EntryStatus, Pagination as PaginationType } from '../types';
import { downloadBulkEntriesPDF } from '../services/api';

interface KnowledgeListProps {
  entries: KnowledgeEntrySummary[];
  pagination?: PaginationType;
  onView: (entryId: string) => void;
  onEdit?: (entryId: string) => void;
  onDelete?: (entryId: string) => void;
  onPageChange?: (page: number) => void;
  loading?: boolean;
  showActions?: boolean;
}

const KnowledgeList: React.FC<KnowledgeListProps> = ({
  entries,
  pagination,
  onView,
  onEdit,
  onDelete,
  onPageChange,
  loading = false,
  showActions = false,
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [bulkDownloadLoading, setBulkDownloadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: EntryStatus) => {
    return status === EntryStatus.PUBLISHED ? 'success' : 'warning';
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedIds(entries.map((entry) => entry.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (entryId: string) => {
    setSelectedIds((prev) =>
      prev.includes(entryId)
        ? prev.filter((id) => id !== entryId)
        : [...prev, entryId]
    );
  };

  const handleBulkDownload = async () => {
    if (selectedIds.length === 0) return;

    setBulkDownloadLoading(true);
    setError(null);

    try {
      await downloadBulkEntriesPDF(selectedIds);
      setSelectedIds([]); // Clear selection after successful download
    } catch (err: any) {
      console.error('Failed to download PDF:', err);
      if (err.response?.status === 403) {
        setError('You do not have permission to download these entries.');
      } else if (err.response?.status === 400) {
        setError('Invalid request. Please try selecting fewer entries.');
      } else {
        setError('Download failed. Please try again.');
      }
    } finally {
      setBulkDownloadLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedIds([]);
  };

  const isSelected = (entryId: string) => selectedIds.includes(entryId);
  const selectAll = selectedIds.length === entries.length && entries.length > 0;
  const someSelected = selectedIds.length > 0 && selectedIds.length < entries.length;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (entries.length === 0) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
            No knowledge entries found.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={2}>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
      {selectedIds.length > 0 && (
        <Box
          sx={{
            p: 2,
            bgcolor: 'primary.light',
            display: 'flex',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Typography variant="body1" color="primary.contrastText">
            {selectedIds.length} item(s) selected
          </Typography>
          <Button
            variant="contained"
            startIcon={bulkDownloadLoading ? <CircularProgress size={20} /> : <PdfIcon />}
            onClick={handleBulkDownload}
            disabled={bulkDownloadLoading}
            sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: 'grey.100' } }}
          >
            {bulkDownloadLoading ? 'Downloading...' : 'Download PDF'}
          </Button>
          <Button
            onClick={clearSelection}
            startIcon={<CloseIcon />}
            sx={{ color: 'primary.contrastText' }}
          >
            Clear
          </Button>
        </Box>
      )}
      <TableContainer component={Paper} elevation={0}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectAll}
                  indeterminate={someSelected}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>MA Name</TableCell>
              <TableCell>Facility</TableCell>
              <TableCell>Specialty Service</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((entry) => (
              <TableRow
                key={entry.id}
                hover
                selected={isSelected(entry.id)}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={isSelected(entry.id)}
                    onChange={() => handleSelectOne(entry.id)}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {entry.ma_name}
                  </Typography>
                </TableCell>
                <TableCell>{entry.facility}</TableCell>
                <TableCell>{entry.specialty_service}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.status}
                    color={getStatusColor(entry.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{formatDate(entry.created_at)}</TableCell>
                <TableCell align="right">
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => onView(entry.id)}
                    >
                      <ViewIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {showActions && onEdit && (
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => onEdit(entry.id)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {showActions && onDelete && (
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => onDelete(entry.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {pagination && pagination.total_pages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <Pagination
            count={pagination.total_pages}
            page={pagination.page}
            onChange={(_, page) => onPageChange?.(page)}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      )}
    </Card>
  );
};

export default KnowledgeList;
