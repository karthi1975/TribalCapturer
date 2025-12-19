/**
 * Specialty Management Component (Creator Only)
 * Allows Creators to manage specialties - create, update, and deactivate.
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
import { getSpecialties, deactivateSpecialty } from '../../services/api';
import { SpecialtyWithCounts } from '../../types';
import SpecialtyFormDialog from './SpecialtyFormDialog';

const SpecialtyManagement: React.FC = () => {
  const [specialties, setSpecialties] = useState<SpecialtyWithCounts[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Dialog states
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [selectedSpecialty, setSelectedSpecialty] = useState<SpecialtyWithCounts | null>(null);

  const pageSize = 50;

  const fetchSpecialties = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getSpecialties(page, pageSize, false); // Show all (active + inactive)
      setSpecialties(response.specialties as SpecialtyWithCounts[]);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / response.page_size));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load specialties');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSpecialties();
  }, [page]);

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleCreate = () => {
    setSelectedSpecialty(null);
    setFormDialogOpen(true);
  };

  const handleEdit = (specialty: SpecialtyWithCounts) => {
    setSelectedSpecialty(specialty);
    setFormDialogOpen(true);
  };

  const handleToggleStatus = async (specialty: SpecialtyWithCounts) => {
    try {
      if (specialty.is_active) {
        // Check if specialty has assigned users or knowledge entries
        if (specialty.assigned_user_count > 0) {
          setError(
            `Cannot deactivate specialty: ${specialty.assigned_user_count} users are assigned to it. Please reassign users first.`
          );
          return;
        }
        if (specialty.knowledge_entry_count > 0) {
          setError(
            `Cannot deactivate specialty: ${specialty.knowledge_entry_count} knowledge entries exist for it.`
          );
          return;
        }
        await deactivateSpecialty(specialty.id);
        setSuccess('Specialty deactivated successfully');
      } else {
        // Reactivate by updating
        const { updateSpecialty } = await import('../../services/api');
        await updateSpecialty(specialty.id, { is_active: true });
        setSuccess('Specialty activated successfully');
      }
      fetchSpecialties();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update specialty status');
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
            <Typography variant="h5">Specialty Management</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Manage medical specialties that MAs can be assigned to
            </Typography>
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
            Add Specialty
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
                  {specialties.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                          No specialties found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    specialties.map((specialty) => (
                      <TableRow key={specialty.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {specialty.name}
                          </Typography>
                        </TableCell>
                        <TableCell>{specialty.code || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={specialty.is_active ? 'Active' : 'Inactive'}
                            size="small"
                            color={specialty.is_active ? 'success' : 'default'}
                          />
                        </TableCell>
                        <TableCell align="center">
                          {specialty.assigned_user_count || 0}
                        </TableCell>
                        <TableCell align="center">
                          {specialty.knowledge_entry_count || 0}
                        </TableCell>
                        <TableCell>{formatDate(specialty.created_at)}</TableCell>
                        <TableCell align="right">
                          <Tooltip title="Edit Specialty">
                            <IconButton size="small" onClick={() => handleEdit(specialty)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={specialty.is_active ? 'Deactivate' : 'Activate'}>
                            <IconButton
                              size="small"
                              onClick={() => handleToggleStatus(specialty)}
                            >
                              {specialty.is_active ? <BlockIcon /> : <CheckCircleIcon />}
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
              Showing {specialties.length} of {total} specialties
            </Typography>
          </>
        )}
      </CardContent>

      {/* Form Dialog */}
      <SpecialtyFormDialog
        specialty={selectedSpecialty}
        open={formDialogOpen}
        onClose={() => {
          setFormDialogOpen(false);
          setSelectedSpecialty(null);
        }}
        onSuccess={() => {
          setFormDialogOpen(false);
          setSelectedSpecialty(null);
          setSuccess(selectedSpecialty ? 'Specialty updated successfully' : 'Specialty created successfully');
          fetchSpecialties();
        }}
      />
    </Card>
  );
};

export default SpecialtyManagement;
