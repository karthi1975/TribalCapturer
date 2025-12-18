/**
 * Material-UI Knowledge List Component
 */
import React from 'react';
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
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { KnowledgeEntrySummary, EntryStatus, Pagination as PaginationType } from '../types';

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
      <TableContainer component={Paper} elevation={0}>
        <Table>
          <TableHead>
            <TableRow>
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
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
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
