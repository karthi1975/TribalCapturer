/**
 * User Edit Dialog Component
 * Allows Creators to edit user details (name and active status).
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
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
} from '@mui/material';
import { updateUser } from '../../services/api';
import { UserDetailWithAssignments, UserUpdateRequest } from '../../types';

interface UserEditDialogProps {
  user: UserDetailWithAssignments | null;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const UserEditDialog: React.FC<UserEditDialogProps> = ({ user, open, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<UserUpdateRequest>({
    full_name: '',
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (user && open) {
      setFormData({
        full_name: user.full_name,
        is_active: user.is_active,
      });
      setErrors({});
      setError(null);
    }
  }, [user, open]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.full_name?.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!user || !validate()) return;

    setLoading(true);
    setError(null);

    try {
      await updateUser(user.id, formData);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit User</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Email"
            value={user.username}
            disabled
            helperText="Email cannot be changed"
          />

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
            label="Role"
            value={user.role}
            disabled
            helperText="Role cannot be changed"
          />

          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                disabled={loading}
              />
            }
            label="Active"
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserEditDialog;
