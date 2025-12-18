/**
 * Batch Knowledge Entry Form Component
 * Allows MAs to create multiple knowledge entries and submit them atomically.
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardHeader,
  CardContent,
  TextField,
  Button,
  Alert,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Checkbox,
  FormControlLabel,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Publish as PublishIcon,
} from '@mui/icons-material';
import { KnowledgeEntryCreateRequest, EntryStatus, KnowledgeType } from '../types';

const FACILITIES = [
  'Intermountain Medical Center – Murray, UT',
  'Primary Children\'s Hospital – Salt Lake City, UT',
  'LDS Hospital – Salt Lake City, UT',
  'McKay-Dee Hospital – Ogden, UT',
  'Utah Valley Hospital – Provo, UT',
  'American Fork Hospital – American Fork, UT',
  'Riverton Hospital – Riverton, UT',
  'Park City Hospital – Park City, UT',
  'Dixie Regional Medical Center – St.George, UT',
  'Logan Regional Hospital – Logan, UT',
];

const KNOWLEDGE_TYPES = [
  {
    value: KnowledgeType.GENERAL_KNOWLEDGE,
    label: 'General Knowledge',
  },
  {
    value: KnowledgeType.DIAGNOSIS_SPECIALTY,
    label: 'Diagnosis → Specialty Referral',
  },
  {
    value: KnowledgeType.PROVIDER_PREFERENCE,
    label: 'Provider Preference',
  },
  {
    value: KnowledgeType.CONTINUITY_CARE,
    label: 'Continuity of Care Rule',
  },
  {
    value: KnowledgeType.PRE_VISIT_REQUIREMENT,
    label: 'Pre-Visit Requirement',
  },
  {
    value: KnowledgeType.SCHEDULING_WORKFLOW,
    label: 'Scheduling Workflow',
  },
];

interface EntryCard {
  id: string;
  data: KnowledgeEntryCreateRequest;
  errors: Partial<KnowledgeEntryCreateRequest>;
}

interface BatchKnowledgeEntryFormProps {
  onSubmit: (entries: KnowledgeEntryCreateRequest[]) => Promise<void>;
}

interface EntryCardProps {
  index: number;
  data: KnowledgeEntryCreateRequest;
  errors: Partial<KnowledgeEntryCreateRequest>;
  canRemove: boolean;
  onUpdate: (data: KnowledgeEntryCreateRequest) => void;
  onRemove: () => void;
  disabled: boolean;
}

const EntryCard: React.FC<EntryCardProps> = ({
  index,
  data,
  errors,
  canRemove,
  onUpdate,
  onRemove,
  disabled,
}) => {
  return (
    <Card elevation={2}>
      <CardHeader
        title={`Entry ${index + 1}`}
        action={
          canRemove && (
            <IconButton onClick={onRemove} disabled={disabled} color="error">
              <DeleteIcon />
            </IconButton>
          )
        }
        sx={{ pb: 1 }}
      />
      <CardContent>
        <Stack spacing={2}>
          {/* Facility Dropdown */}
          <FormControl fullWidth required error={!!errors.facility} disabled={disabled}>
            <InputLabel>Facility</InputLabel>
            <Select
              value={data.facility}
              label="Facility"
              onChange={(e) => onUpdate({ ...data, facility: e.target.value })}
            >
              {FACILITIES.map((facility) => (
                <MenuItem key={facility} value={facility}>
                  {facility}
                </MenuItem>
              ))}
            </Select>
            {errors.facility && <FormHelperText>{errors.facility}</FormHelperText>}
          </FormControl>

          {/* Specialty Service */}
          <TextField
            fullWidth
            required
            label="Specialty Service"
            value={data.specialty_service}
            onChange={(e) => onUpdate({ ...data, specialty_service: e.target.value })}
            error={!!errors.specialty_service}
            helperText={errors.specialty_service}
            disabled={disabled}
            placeholder="e.g., Cardiology, Orthopedics"
          />

          {/* Provider Name */}
          <TextField
            fullWidth
            label="Provider Name (Optional)"
            value={data.provider_name || ''}
            onChange={(e) => onUpdate({ ...data, provider_name: e.target.value })}
            disabled={disabled}
            placeholder="e.g., Dr. Smith"
          />

          {/* Knowledge Type */}
          <FormControl fullWidth disabled={disabled}>
            <InputLabel>Knowledge Type</InputLabel>
            <Select
              value={data.knowledge_type}
              label="Knowledge Type"
              onChange={(e) => onUpdate({ ...data, knowledge_type: e.target.value as KnowledgeType })}
            >
              {KNOWLEDGE_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Continuity Care Checkbox */}
          <FormControlLabel
            control={
              <Checkbox
                checked={data.is_continuity_care}
                onChange={(e) => onUpdate({ ...data, is_continuity_care: e.target.checked })}
                disabled={disabled}
              />
            }
            label="Continuity of care"
          />

          {/* Knowledge Description */}
          <TextField
            fullWidth
            required
            multiline
            rows={4}
            label="Knowledge Description"
            value={data.knowledge_description}
            onChange={(e) => onUpdate({ ...data, knowledge_description: e.target.value })}
            error={!!errors.knowledge_description}
            helperText={errors.knowledge_description || 'Min 10 characters'}
            disabled={disabled}
            placeholder="Describe the tribal knowledge in detail..."
          />
        </Stack>
      </CardContent>
    </Card>
  );
};

const BatchKnowledgeEntryForm: React.FC<BatchKnowledgeEntryFormProps> = ({ onSubmit }) => {
  const createNewEntryCard = (): EntryCard => ({
    id: crypto.randomUUID(),
    data: {
      facility: '',
      specialty_service: '',
      provider_name: '',
      knowledge_type: KnowledgeType.GENERAL_KNOWLEDGE,
      is_continuity_care: false,
      knowledge_description: '',
      status: EntryStatus.PUBLISHED,
    },
    errors: {},
  });

  const [entryCards, setEntryCards] = useState<EntryCard[]>([createNewEntryCard()]);
  const [loading, setLoading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleAddEntry = () => {
    setEntryCards([...entryCards, createNewEntryCard()]);
  };

  const handleRemoveEntry = (id: string) => {
    if (entryCards.length > 1) {
      setEntryCards(entryCards.filter(card => card.id !== id));
    }
  };

  const handleUpdateEntry = (id: string, data: KnowledgeEntryCreateRequest) => {
    setEntryCards(entryCards.map(card =>
      card.id === id ? { ...card, data } : card
    ));
  };

  const validateEntry = (data: KnowledgeEntryCreateRequest): Partial<KnowledgeEntryCreateRequest> => {
    const errors: Partial<KnowledgeEntryCreateRequest> = {};
    if (!data.facility.trim()) errors.facility = 'Required';
    if (!data.specialty_service.trim()) errors.specialty_service = 'Required';
    if (!data.knowledge_description.trim()) errors.knowledge_description = 'Required';
    else if (data.knowledge_description.trim().length < 10) {
      errors.knowledge_description = 'Min 10 characters';
    }
    return errors;
  };

  const validateAllEntries = (): boolean => {
    const updatedCards = entryCards.map(card => ({
      ...card,
      errors: validateEntry(card.data),
    }));
    setEntryCards(updatedCards);
    return updatedCards.every(card => Object.keys(card.errors).length === 0);
  };

  const handleSubmitAll = async () => {
    setGlobalError(null);
    setSuccess(false);

    if (!validateAllEntries()) {
      setGlobalError('Please fix validation errors in all entries');
      return;
    }

    setLoading(true);
    try {
      const entries = entryCards.map(card => card.data);
      await onSubmit(entries);
      setSuccess(true);
      // Reset form - start with one empty entry
      setEntryCards([createNewEntryCard()]);
    } catch (error: any) {
      setGlobalError(error.message || 'Failed to submit entries');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Success Alert */}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(false)}>
          All knowledge entries submitted successfully!
        </Alert>
      )}

      {/* Error Alert */}
      {globalError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setGlobalError(null)}>
          {globalError}
        </Alert>
      )}

      {/* Entry Cards */}
      <Stack spacing={3}>
        {entryCards.map((card, index) => (
          <EntryCard
            key={card.id}
            index={index}
            data={card.data}
            errors={card.errors}
            canRemove={entryCards.length > 1}
            onUpdate={(data) => handleUpdateEntry(card.id, data)}
            onRemove={() => handleRemoveEntry(card.id)}
            disabled={loading}
          />
        ))}
      </Stack>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddEntry}
          disabled={loading || entryCards.length >= 50}
        >
          Add Another Entry
        </Button>
        <Button
          variant="contained"
          size="large"
          startIcon={<PublishIcon />}
          onClick={handleSubmitAll}
          disabled={loading || entryCards.length === 0}
        >
          {loading ? 'Submitting...' : `Submit All (${entryCards.length})`}
        </Button>
      </Box>
    </Box>
  );
};

export default BatchKnowledgeEntryForm;
