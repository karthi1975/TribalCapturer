/**
 * User Create Dialog Component
 * Allows Creators to create new MA or Creator users with optional assignments.
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Alert,
  CircularProgress,
} from '@mui/material';
import { createUser, getFacilities, getSpecialties } from '../../services/api';
import { UserRole, UserCreateRequest, Facility, Specialty } from '../../types';

interface UserCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const UserCreateDialog: React.FC<UserCreateDialogProps> = ({ open, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<UserCreateRequest>({
    username: '',
    password: '',
    full_name: '',
    role: UserRole.MA,
    facility_ids: [],
    specialty_ids: [],
  });
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) {
      fetchFacilitiesAndSpecialties();
      // Reset form when dialog opens
      setFormData({
        username: '',
        password: '',
        full_name: '',
        role: UserRole.MA,
        facility_ids: [],
        specialty_ids: [],
      });
      setErrors({});
      setError(null);
    }
  }, [open]);

  const fetchFacilitiesAndSpecialties = async () => {
    try {
      const [facilitiesRes, specialtiesRes] = await Promise.all([
        getFacilities(1, 100, true),
        getSpecialties(1, 100, true),
      ]);
      setFacilities(facilitiesRes.facilities);
      setSpecialties(specialtiesRes.specialties);
    } catch (err: any) {
      setError('Failed to load facilities and specialties');
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    if (!formData.username.trim()) {
      newErrors.username = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.username)) {
      newErrors.username = 'Invalid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 12) {
      newErrors.password = 'Password must be at least 12 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    setError(null);

    try {
      await createUser(formData);
      onSuccess();
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('A user with this email already exists');
      } else {
        setError(err.response?.data?.detail || 'Failed to create user');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (role: UserRole) => {
    setFormData({
      ...formData,
      role,
      // Clear assignments when switching to Creator role
      facility_ids: role === UserRole.CREATOR ? [] : formData.facility_ids,
      specialty_ids: role === UserRole.CREATOR ? [] : formData.specialty_ids,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New User</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Full Name"
            required
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            error={!!errors.full_name}
            helperText={errors.full_name}
            disabled={loading}
          />

          <TextField
            label="Email"
            type="email"
            required
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            error={!!errors.username}
            helperText={errors.username}
            disabled={loading}
          />

          <TextField
            label="Password"
            type="password"
            required
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            error={!!errors.password}
            helperText={errors.password || 'Minimum 12 characters'}
            disabled={loading}
          />

          <FormControl required disabled={loading}>
            <InputLabel>Role</InputLabel>
            <Select value={formData.role} onChange={(e) => handleRoleChange(e.target.value as UserRole)}>
              <MenuItem value={UserRole.MA}>Medical Assistant</MenuItem>
              <MenuItem value={UserRole.CREATOR}>Creator</MenuItem>
            </Select>
          </FormControl>

          {formData.role === UserRole.MA && (
            <>
              <Autocomplete
                multiple
                options={facilities}
                getOptionLabel={(option) => option.name}
                value={facilities.filter((f) => formData.facility_ids?.includes(f.id))}
                onChange={(_, newValue) =>
                  setFormData({ ...formData, facility_ids: newValue.map((f) => f.id) })
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Assign Facilities"
                    placeholder="Select facilities (optional)"
                    helperText="You can assign facilities now or later"
                  />
                )}
                disabled={loading}
              />

              <Autocomplete
                multiple
                options={specialties}
                getOptionLabel={(option) => option.name}
                value={specialties.filter((s) => formData.specialty_ids?.includes(s.id))}
                onChange={(_, newValue) =>
                  setFormData({ ...formData, specialty_ids: newValue.map((s) => s.id) })
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Assign Specialties"
                    placeholder="Select specialties (optional)"
                    helperText="You can assign specialties now or later"
                  />
                )}
                disabled={loading}
              />
            </>
          )}

          {formData.role === UserRole.CREATOR && (
            <Alert severity="info">
              Creator users have full access to all features and do not need facility/specialty
              assignments.
            </Alert>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Create User'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserCreateDialog;
