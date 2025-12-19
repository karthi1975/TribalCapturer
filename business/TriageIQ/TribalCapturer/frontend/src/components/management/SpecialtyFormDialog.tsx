/**
 * Specialty Form Dialog Component
 * Create or edit specialty details.
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
import { createSpecialty, updateSpecialty } from '../../services/api';
import {
  SpecialtyWithCounts,
  SpecialtyCreateRequest,
  SpecialtyUpdateRequest,
} from '../../types';

interface SpecialtyFormDialogProps {
  specialty: SpecialtyWithCounts | null;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const SpecialtyFormDialog: React.FC<SpecialtyFormDialogProps> = ({
  specialty,
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

  const isEdit = !!specialty;

  useEffect(() => {
    if (specialty && open) {
      setFormData({
        name: specialty.name,
        code: specialty.code || '',
      });
      setErrors({});
      setError(null);
    } else if (!specialty && open) {
      setFormData({
        name: '',
        code: '',
      });
      setErrors({});
      setError(null);
    }
  }, [specialty, open]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Specialty name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    setError(null);

    try {
      if (isEdit && specialty) {
        const updateData: SpecialtyUpdateRequest = {
          name: formData.name.trim(),
          code: formData.code.trim() || undefined,
        };
        await updateSpecialty(specialty.id, updateData);
      } else {
        const createData: SpecialtyCreateRequest = {
          name: formData.name.trim(),
          code: formData.code.trim() || undefined,
        };
        await createSpecialty(createData);
      }
      onSuccess();
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('A specialty with this name already exists');
      } else {
        setError(err.response?.data?.detail || `Failed to ${isEdit ? 'update' : 'create'} specialty`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? 'Edit Specialty' : 'Create New Specialty'}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Specialty Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={!!errors.name}
            helperText={errors.name || 'e.g., Cardiology, Pediatrics, Orthopedics'}
            disabled={loading}
          />

          <TextField
            label="Specialty Code"
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
          {loading ? <CircularProgress size={24} /> : isEdit ? 'Save Changes' : 'Create Specialty'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SpecialtyFormDialog;
