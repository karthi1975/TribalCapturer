/**
 * User Management Component (Creator Only)
 * Allows Creators to manage MA and Creator users, including CRUD operations,
 * activation/deactivation, password resets, and facility/specialty assignments.
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
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  Edit as EditIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
  LockReset as LockResetIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import {
  getUsers,
  activateUser,
  deactivateUser,
  resetUserPassword,
} from '../../services/api';
import { UserDetailWithAssignments, UserRole } from '../../types';
import UserCreateDialog from './UserCreateDialog';
import UserEditDialog from './UserEditDialog';
import UserAssignmentDialog from './UserAssignmentDialog';

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<UserDetailWithAssignments[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('');
  const [statusFilter, setStatusFilter] = useState<boolean | null>(true);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  const [passwordResetDialogOpen, setPasswordResetDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserDetailWithAssignments | null>(null);
  const [newPassword, setNewPassword] = useState('');

  const pageSize = 20;

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getUsers(
        page,
        pageSize,
        roleFilter || undefined,
        statusFilter ?? true
      );
      setUsers(response.users);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / response.page_size));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter, statusFilter]);

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleRoleFilterChange = (event: any) => {
    setRoleFilter(event.target.value);
    setPage(1);
  };

  const handleStatusFilterChange = (event: any) => {
    const value = event.target.value;
    setStatusFilter(value === 'all' ? null : value === 'active');
    setPage(1);
  };

  const handleCreateUser = () => {
    setCreateDialogOpen(true);
  };

  const handleEditUser = (user: UserDetailWithAssignments) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };

  const handleManageAssignments = (user: UserDetailWithAssignments) => {
    setSelectedUser(user);
    setAssignmentDialogOpen(true);
  };

  const handleResetPassword = (user: UserDetailWithAssignments) => {
    setSelectedUser(user);
    setNewPassword('');
    setPasswordResetDialogOpen(true);
  };

  const handleToggleUserStatus = async (userId: string, isActive: boolean) => {
    try {
      if (isActive) {
        await deactivateUser(userId);
        setSuccess('User deactivated successfully');
      } else {
        await activateUser(userId);
        setSuccess('User activated successfully');
      }
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user status');
    }
  };

  const handlePasswordResetSubmit = async () => {
    if (!selectedUser || !newPassword) return;

    if (newPassword.length < 12) {
      setError('Password must be at least 12 characters');
      return;
    }

    try {
      await resetUserPassword(selectedUser.id, { new_password: newPassword });
      setSuccess('Password reset successfully');
      setPasswordResetDialogOpen(false);
      setSelectedUser(null);
      setNewPassword('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5" component="h2">
            User Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={handleCreateUser}
          >
            Create User
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

        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Role</InputLabel>
            <Select value={roleFilter} onChange={handleRoleFilterChange}>
              <MenuItem value="">All Roles</MenuItem>
              <MenuItem value={UserRole.MA}>Medical Assistant</MenuItem>
              <MenuItem value={UserRole.CREATOR}>Creator</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter === null ? 'all' : statusFilter ? 'active' : 'inactive'}
              onChange={handleStatusFilterChange}
            >
              <MenuItem value="active">Active Only</MenuItem>
              <MenuItem value="inactive">Inactive Only</MenuItem>
              <MenuItem value="all">All Users</MenuItem>
            </Select>
          </FormControl>
        </Stack>

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
                    <TableCell>Email</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Facilities</TableCell>
                    <TableCell>Specialties</TableCell>
                    <TableCell>Last Login</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                          No users found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    users.map((user) => (
                      <TableRow key={user.id} hover>
                        <TableCell>{user.full_name}</TableCell>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>
                          <Chip
                            label={user.role}
                            size="small"
                            color={user.role === UserRole.MA ? 'primary' : 'secondary'}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={user.is_active ? 'Active' : 'Inactive'}
                            size="small"
                            color={user.is_active ? 'success' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          {user.assigned_facilities.length > 0 ? (
                            <Tooltip
                              title={user.assigned_facilities.map((f) => f.name).join(', ')}
                            >
                              <Chip
                                label={`${user.assigned_facilities.length} facilities`}
                                size="small"
                                variant="outlined"
                              />
                            </Tooltip>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>
                          {user.assigned_specialties.length > 0 ? (
                            <Tooltip
                              title={user.assigned_specialties.map((s) => s.name).join(', ')}
                            >
                              <Chip
                                label={`${user.assigned_specialties.length} specialties`}
                                size="small"
                                variant="outlined"
                              />
                            </Tooltip>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>{formatDate(user.last_login)}</TableCell>
                        <TableCell align="right">
                          <Tooltip title="Manage Assignments">
                            <IconButton
                              size="small"
                              onClick={() => handleManageAssignments(user)}
                              disabled={user.role !== UserRole.MA}
                            >
                              <AssignmentIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit User">
                            <IconButton size="small" onClick={() => handleEditUser(user)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={user.is_active ? 'Deactivate' : 'Activate'}>
                            <IconButton
                              size="small"
                              onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                            >
                              {user.is_active ? <BlockIcon /> : <CheckCircleIcon />}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reset Password">
                            <IconButton size="small" onClick={() => handleResetPassword(user)}>
                              <LockResetIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>

            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
              Showing {users.length} of {total} users
            </Typography>
          </>
        )}
      </CardContent>

      {/* Dialogs */}
      <UserCreateDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={() => {
          setCreateDialogOpen(false);
          setSuccess('User created successfully');
          fetchUsers();
        }}
      />

      <UserEditDialog
        user={selectedUser}
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false);
          setSelectedUser(null);
        }}
        onSuccess={() => {
          setEditDialogOpen(false);
          setSelectedUser(null);
          setSuccess('User updated successfully');
          fetchUsers();
        }}
      />

      <UserAssignmentDialog
        user={selectedUser}
        open={assignmentDialogOpen}
        onClose={() => {
          setAssignmentDialogOpen(false);
          setSelectedUser(null);
        }}
        onSuccess={() => {
          setAssignmentDialogOpen(false);
          setSelectedUser(null);
          setSuccess('Assignments updated successfully');
          fetchUsers();
        }}
      />

      {/* Password Reset Dialog */}
      <Dialog open={passwordResetDialogOpen} onClose={() => setPasswordResetDialogOpen(false)}>
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Reset password for <strong>{selectedUser?.full_name}</strong> ({selectedUser?.username})
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="New Password"
            type="password"
            fullWidth
            variant="outlined"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            helperText="Minimum 12 characters"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordResetDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handlePasswordResetSubmit}
            variant="contained"
            disabled={newPassword.length < 12}
          >
            Reset Password
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default UserManagement;
