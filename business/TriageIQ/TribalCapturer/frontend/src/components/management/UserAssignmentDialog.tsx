/**
 * User Assignment Dialog Component
 * Allows Creators to manage facility and specialty assignments for MA users.
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stack,
  Autocomplete,
  TextField,
  Alert,
  CircularProgress,
  Typography,
  Chip,
} from '@mui/material';
import {
  updateUserAssignments,
  getFacilities,
  getSpecialties,
} from '../../services/api';
import { UserDetailWithAssignments, Facility, Specialty } from '../../types';

interface UserAssignmentDialogProps {
  user: UserDetailWithAssignments | null;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const UserAssignmentDialog: React.FC<UserAssignmentDialogProps> = ({
  user,
  open,
  onClose,
  onSuccess,
}) => {
  const [selectedFacilities, setSelectedFacilities] = useState<Facility[]>([]);
  const [selectedSpecialties, setSelectedSpecialties] = useState<Specialty[]>([]);
  const [allFacilities, setAllFacilities] = useState<Facility[]>([]);
  const [allSpecialties, setAllSpecialties] = useState<Specialty[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      fetchFacilitiesAndSpecialties();
    }
  }, [open]);

  useEffect(() => {
    if (user && open) {
      setSelectedFacilities(user.assigned_facilities || []);
      setSelectedSpecialties(user.assigned_specialties || []);
      setError(null);
    }
  }, [user, open]);

  const fetchFacilitiesAndSpecialties = async () => {
    try {
      const [facilitiesRes, specialtiesRes] = await Promise.all([
        getFacilities(1, 100, true),
        getSpecialties(1, 100, true),
      ]);
      setAllFacilities(facilitiesRes.facilities);
      setAllSpecialties(specialtiesRes.specialties);
    } catch (err: any) {
      setError('Failed to load facilities and specialties');
    }
  };

  const handleSubmit = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      await updateUserAssignments(user.id, {
        facility_ids: selectedFacilities.map((f) => f.id),
        specialty_ids: selectedSpecialties.map((s) => s.id),
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update assignments');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Manage Assignments for {user.full_name}
        <Typography variant="caption" display="block" color="text.secondary">
          {user.username}
        </Typography>
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Alert severity="info" sx={{ mb: 3 }}>
          MAs can only create knowledge entries for their assigned facilities and specialties.
          Selecting no assignments will prevent the MA from creating any entries.
        </Alert>

        <Stack spacing={3} sx={{ mt: 2 }}>
          <Autocomplete
            multiple
            options={allFacilities}
            getOptionLabel={(option) => option.name}
            value={selectedFacilities}
            onChange={(_, newValue) => setSelectedFacilities(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Assigned Facilities"
                placeholder="Select facilities"
                helperText={`${selectedFacilities.length} facilities selected`}
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option.name}
                  {...getTagProps({ index })}
                  size="small"
                />
              ))
            }
            disabled={loading}
          />

          <Autocomplete
            multiple
            options={allSpecialties}
            getOptionLabel={(option) => option.name}
            value={selectedSpecialties}
            onChange={(_, newValue) => setSelectedSpecialties(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Assigned Specialties"
                placeholder="Select specialties"
                helperText={`${selectedSpecialties.length} specialties selected`}
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option.name}
                  {...getTagProps({ index })}
                  size="small"
                />
              ))
            }
            disabled={loading}
          />

          {selectedFacilities.length === 0 && selectedSpecialties.length === 0 && (
            <Alert severity="warning">
              This user will not be able to create any knowledge entries without assignments.
            </Alert>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Save Assignments'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserAssignmentDialog;
