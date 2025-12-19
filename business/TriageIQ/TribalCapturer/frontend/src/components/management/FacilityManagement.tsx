/**
 * Facility Management Component (Creator Only)
 * Allows Creators to manage facilities - create, update, and deactivate.
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Pagination,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { getFacilities, deactivateFacility } from '../../services/api';
import { FacilityWithCounts } from '../../types';
import FacilityFormDialog from './FacilityFormDialog';

const FacilityManagement: React.FC = () => {
  const [facilities, setFacilities] = useState<FacilityWithCounts[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Dialog states
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [selectedFacility, setSelectedFacility] = useState<FacilityWithCounts | null>(null);

  const pageSize = 50;

  const fetchFacilities = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getFacilities(page, pageSize, false); // Show all (active + inactive)
      setFacilities(response.facilities as FacilityWithCounts[]);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / response.page_size));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load facilities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacilities();
  }, [page]);

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleCreate = () => {
    setSelectedFacility(null);
    setFormDialogOpen(true);
  };

  const handleEdit = (facility: FacilityWithCounts) => {
    setSelectedFacility(facility);
    setFormDialogOpen(true);
  };

  const handleToggleStatus = async (facility: FacilityWithCounts) => {
    try {
      if (facility.is_active) {
        // Check if facility has assigned users or knowledge entries
        if (facility.assigned_user_count > 0) {
          setError(
            `Cannot deactivate facility: ${facility.assigned_user_count} users are assigned to it. Please reassign users first.`
          );
          return;
        }
        if (facility.knowledge_entry_count > 0) {
          setError(
            `Cannot deactivate facility: ${facility.knowledge_entry_count} knowledge entries exist for it.`
          );
          return;
        }
        await deactivateFacility(facility.id);
        setSuccess('Facility deactivated successfully');
      } else {
        // Reactivate by updating
        const { updateFacility } = await import('../../services/api');
        await updateFacility(facility.id, { is_active: true });
        setSuccess('Facility activated successfully');
      }
      fetchFacilities();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update facility status');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Box>
            <Typography variant="h5">Facility Management</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Manage healthcare facilities that MAs can be assigned to
            </Typography>
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
            Add Facility
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Code</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center"># Assigned MAs</TableCell>
                    <TableCell align="center"># Knowledge Entries</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {facilities.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                          No facilities found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    facilities.map((facility) => (
                      <TableRow key={facility.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {facility.name}
                          </Typography>
                        </TableCell>
                        <TableCell>{facility.code || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={facility.is_active ? 'Active' : 'Inactive'}
                            size="small"
                            color={facility.is_active ? 'success' : 'default'}
                          />
                        </TableCell>
                        <TableCell align="center">
                          {facility.assigned_user_count || 0}
                        </TableCell>
                        <TableCell align="center">
                          {facility.knowledge_entry_count || 0}
                        </TableCell>
                        <TableCell>{formatDate(facility.created_at)}</TableCell>
                        <TableCell align="right">
                          <Tooltip title="Edit Facility">
                            <IconButton size="small" onClick={() => handleEdit(facility)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={facility.is_active ? 'Deactivate' : 'Activate'}>
                            <IconButton
                              size="small"
                              onClick={() => handleToggleStatus(facility)}
                            >
                              {facility.is_active ? <BlockIcon /> : <CheckCircleIcon />}
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}

            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
              Showing {facilities.length} of {total} facilities
            </Typography>
          </>
        )}
      </CardContent>

      {/* Form Dialog */}
      <FacilityFormDialog
        facility={selectedFacility}
        open={formDialogOpen}
        onClose={() => {
          setFormDialogOpen(false);
          setSelectedFacility(null);
        }}
        onSuccess={() => {
          setFormDialogOpen(false);
          setSelectedFacility(null);
          setSuccess(selectedFacility ? 'Facility updated successfully' : 'Facility created successfully');
          fetchFacilities();
        }}
      />
    </Card>
  );
};

export default FacilityManagement;
