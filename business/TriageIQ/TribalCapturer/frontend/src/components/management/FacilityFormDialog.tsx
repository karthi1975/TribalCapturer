/**
 * Facility Form Dialog Component
 * Create or edit facility details.
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
  Alert,
  CircularProgress,
} from '@mui/material';
import { createFacility, updateFacility } from '../../services/api';
import {
  FacilityWithCounts,
  FacilityCreateRequest,
  FacilityUpdateRequest,
} from '../../types';

interface FacilityFormDialogProps {
  facility: FacilityWithCounts | null;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const FacilityFormDialog: React.FC<FacilityFormDialogProps> = ({
  facility,
  open,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    code: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEdit = !!facility;

  useEffect(() => {
    if (facility && open) {
      setFormData({
        name: facility.name,
        code: facility.code || '',
      });
      setErrors({});
      setError(null);
    } else if (!facility && open) {
      setFormData({
        name: '',
        code: '',
      });
      setErrors({});
      setError(null);
    }
  }, [facility, open]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Facility name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    setError(null);

    try {
      if (isEdit && facility) {
        const updateData: FacilityUpdateRequest = {
          name: formData.name.trim(),
          code: formData.code.trim() || undefined,
        };
        await updateFacility(facility.id, updateData);
      } else {
        const createData: FacilityCreateRequest = {
          name: formData.name.trim(),
          code: formData.code.trim() || undefined,
        };
        await createFacility(createData);
      }
      onSuccess();
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('A facility with this name already exists');
      } else {
        setError(err.response?.data?.detail || `Failed to ${isEdit ? 'update' : 'create'} facility`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? 'Edit Facility' : 'Create New Facility'}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Facility Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={!!errors.name}
            helperText={errors.name || 'e.g., Intermountain Medical Center – Murray, UT'}
            disabled={loading}
          />

          <TextField
            label="Facility Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            helperText="Optional short code for internal use"
            disabled={loading}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : isEdit ? 'Save Changes' : 'Create Facility'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FacilityFormDialog;
