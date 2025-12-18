/**
 * Material-UI Knowledge Detail Component (Modal/Dialog)
 */
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Chip,
  Box,
  Stack,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  Person as PersonIcon,
  Business as FacilityIcon,
  LocalHospital as SpecialtyIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { KnowledgeEntry, EntryStatus } from '../types';

interface KnowledgeDetailProps {
  entry: KnowledgeEntry | null;
  open: boolean;
  onClose: () => void;
  loading?: boolean;
}

const KnowledgeDetail: React.FC<KnowledgeDetailProps> = ({
  entry,
  open,
  onClose,
  loading = false,
}) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: EntryStatus) => {
    return status === EntryStatus.PUBLISHED ? 'success' : 'warning';
  };

  const InfoRow: React.FC<{ icon: React.ReactNode; label: string; value: string }> = ({
    icon,
    label,
    value,
  }) => (
    <Stack direction="row" spacing={1} alignItems="center">
      {icon}
      <Typography variant="body2" color="text.secondary">
        {label}:
      </Typography>
      <Typography variant="body2" fontWeight="medium">
        {value}
      </Typography>
    </Stack>
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        elevation: 3,
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5" component="span" color="primary">
            Knowledge Entry Details
          </Typography>
          {entry && (
            <Chip label={entry.status} color={getStatusColor(entry.status)} size="small" />
          )}
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : entry ? (
          <Stack spacing={3}>
            <Stack spacing={1.5}>
              <InfoRow
                icon={<PersonIcon fontSize="small" color="action" />}
                label="Medical Assistant"
                value={entry.ma_name}
              />
              <InfoRow
                icon={<FacilityIcon fontSize="small" color="action" />}
                label="Facility"
                value={entry.facility}
              />
              <InfoRow
                icon={<SpecialtyIcon fontSize="small" color="action" />}
                label="Specialty Service"
                value={entry.specialty_service}
              />
              <InfoRow
                icon={<CalendarIcon fontSize="small" color="action" />}
                label="Created"
                value={formatDate(entry.created_at)}
              />
              {entry.updated_at && (
                <InfoRow
                  icon={<CalendarIcon fontSize="small" color="action" />}
                  label="Last Updated"
                  value={formatDate(entry.updated_at)}
                />
              )}
            </Stack>

            <Divider />

            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="primary">
                Knowledge Description
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-wrap',
                  backgroundColor: 'grey.50',
                  p: 2,
                  borderRadius: 1,
                  border: 1,
                  borderColor: 'divider',
                }}
              >
                {entry.knowledge_description}
              </Typography>
            </Box>
          </Stack>
        ) : (
          <Typography variant="body1" color="text.secondary" align="center">
            No entry selected.
          </Typography>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} startIcon={<CloseIcon />} variant="outlined">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KnowledgeDetail;
