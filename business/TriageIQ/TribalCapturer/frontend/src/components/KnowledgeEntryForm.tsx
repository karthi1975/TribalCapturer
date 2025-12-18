/**
 * Material-UI Knowledge Entry Form Component
 */
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  TextField,
  Button,
  Typography,
  Alert,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Checkbox,
  FormControlLabel,
  Tooltip,
} from '@mui/material';
import { Save as SaveIcon, Publish as PublishIcon } from '@mui/icons-material';
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
    description: 'General tribal knowledge',
    example: 'Friday afternoon appointments: Last slots are 3 PM because lab closes at 4 PM. Patients often need bloodwork after visit.'
  },
  {
    value: KnowledgeType.DIAGNOSIS_SPECIALTY,
    label: 'Diagnosis → Specialty Referral',
    description: 'Maps diagnosis to specialty (e.g., Crohn\'s → Rheumatology)',
    example: 'Patient with new diagnosis of Crohn\'s disease needs Rheumatologist. Check if GI consult completed first - many doctors want GI evaluation before rheumatology referral.'
  },
  {
    value: KnowledgeType.PROVIDER_PREFERENCE,
    label: 'Provider Preference',
    description: 'Provider-specific preferences or requirements',
    example: 'Dr. Smith prefers new patients in afternoon slots (after 1 PM) because she reviews charts in the morning. Complex cases need 60-minute appointments.'
  },
  {
    value: KnowledgeType.CONTINUITY_CARE,
    label: 'Continuity of Care Rule',
    description: 'Rules about seeing same provider again',
    example: 'Post-surgical follow-ups MUST be with the surgeon who performed the procedure. Don\'t schedule with different surgeon in same specialty.'
  },
  {
    value: KnowledgeType.PRE_VISIT_REQUIREMENT,
    label: 'Pre-Visit Requirement',
    description: 'What patient needs before appointment (labs, etc.)',
    example: 'Heart failure follow-ups: BNP labs must be drawn within 48 hours before appointment. Also need current weight, BP log from home monitoring.'
  },
  {
    value: KnowledgeType.SCHEDULING_WORKFLOW,
    label: 'Scheduling Workflow',
    description: 'Scheduling workflow tips and best practices',
    example: 'For bariatric surgery consults: (1) Verify insurance pre-auth, (2) Schedule nutrition consult FIRST, (3) Then surgeon consult 2-4 weeks later.'
  },
];

interface KnowledgeEntryFormProps {
  onSubmit: (data: KnowledgeEntryCreateRequest, isDraft: boolean) => Promise<void>;
  initialData?: Partial<KnowledgeEntryCreateRequest>;
}

const KnowledgeEntryForm: React.FC<KnowledgeEntryFormProps> = ({
  onSubmit,
  initialData,
}) => {
  const [formData, setFormData] = useState<KnowledgeEntryCreateRequest>({
    facility: initialData?.facility || '',
    specialty_service: initialData?.specialty_service || '',
    provider_name: initialData?.provider_name || '',
    knowledge_type: initialData?.knowledge_type || KnowledgeType.GENERAL_KNOWLEDGE,
    is_continuity_care: initialData?.is_continuity_care || false,
    knowledge_description: initialData?.knowledge_description || '',
    status: initialData?.status || EntryStatus.PUBLISHED,
  });

  const [errors, setErrors] = useState<Partial<KnowledgeEntryCreateRequest>>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<KnowledgeEntryCreateRequest> = {};

    if (!formData.facility.trim()) {
      newErrors.facility = 'Facility is required';
    }
    if (!formData.specialty_service.trim()) {
      newErrors.specialty_service = 'Specialty service is required';
    }
    if (!formData.knowledge_description.trim()) {
      newErrors.knowledge_description = 'Knowledge description is required';
    } else if (formData.knowledge_description.trim().length < 10) {
      newErrors.knowledge_description = 'Description must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (isDraft: boolean) => {
    if (!validate()) return;

    setLoading(true);
    setSuccess(false);

    try {
      const submitData = {
        ...formData,
        status: isDraft ? EntryStatus.DRAFT : EntryStatus.PUBLISHED,
      };
      await onSubmit(submitData, isDraft);
      setSuccess(true);
      // Reset form after successful submission
      if (!isDraft) {
        setFormData({
          facility: '',
          specialty_service: '',
          provider_name: '',
          knowledge_type: KnowledgeType.GENERAL_KNOWLEDGE,
          is_continuity_care: false,
          knowledge_description: '',
          status: EntryStatus.PUBLISHED,
        });
      }
    } catch (error) {
      console.error('Submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h5" gutterBottom color="primary">
          Capture Tribal Knowledge
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Share your insights about clinic operations, scheduling practices, and workflows.
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
            Knowledge entry saved successfully!
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 2 }}>
          <FormControl fullWidth required error={!!errors.facility} disabled={loading}>
            <InputLabel id="facility-label">Facility</InputLabel>
            <Select
              labelId="facility-label"
              id="facility"
              value={formData.facility}
              label="Facility"
              onChange={(e) => setFormData({ ...formData, facility: e.target.value })}
            >
              {FACILITIES.map((facility) => (
                <MenuItem key={facility} value={facility}>
                  {facility}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>{errors.facility || 'Select your facility'}</FormHelperText>
          </FormControl>

          <TextField
            fullWidth
            label="Specialty Service"
            value={formData.specialty_service}
            onChange={(e) =>
              setFormData({ ...formData, specialty_service: e.target.value })
            }
            error={!!errors.specialty_service}
            helperText={errors.specialty_service || 'e.g., Cardiology, Emergency Medicine'}
            required
            disabled={loading}
          />

          <TextField
            fullWidth
            label="Provider Name (Optional)"
            value={formData.provider_name}
            onChange={(e) =>
              setFormData({ ...formData, provider_name: e.target.value })
            }
            helperText="Specific provider this knowledge applies to (e.g., Dr. Smith)"
            disabled={loading}
          />

          <FormControl fullWidth disabled={loading}>
            <InputLabel id="knowledge-type-label">Knowledge Type</InputLabel>
            <Select
              labelId="knowledge-type-label"
              id="knowledge-type"
              value={formData.knowledge_type}
              label="Knowledge Type"
              onChange={(e) =>
                setFormData({ ...formData, knowledge_type: e.target.value as KnowledgeType })
              }
            >
              {KNOWLEDGE_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  <Tooltip title={type.description} placement="right">
                    <span>{type.label}</span>
                  </Tooltip>
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              What category does this knowledge fall into? (Helps AI route scheduling decisions)
            </FormHelperText>
          </FormControl>

          <FormControlLabel
            control={
              <Checkbox
                checked={formData.is_continuity_care}
                onChange={(e) =>
                  setFormData({ ...formData, is_continuity_care: e.target.checked })
                }
                disabled={loading}
              />
            }
            label="This is about continuity of care (seeing the same provider again)"
          />

          <TextField
            fullWidth
            label="Knowledge Description"
            value={formData.knowledge_description}
            onChange={(e) =>
              setFormData({ ...formData, knowledge_description: e.target.value })
            }
            error={!!errors.knowledge_description}
            helperText={
              errors.knowledge_description ||
              'Describe the tribal knowledge in detail. Minimum 10 characters.'
            }
            required
            multiline
            rows={8}
            disabled={loading}
            placeholder="Example: When scheduling follow-up appointments for heart failure patients, always check if they need lab work first. Dr. Johnson prefers to review recent BNP levels before the appointment..."
          />
        </Stack>
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
        <Button
          variant="outlined"
          startIcon={<SaveIcon />}
          onClick={() => handleSubmit(true)}
          disabled={loading}
        >
          Save Draft
        </Button>
        <Button
          variant="contained"
          startIcon={<PublishIcon />}
          onClick={() => handleSubmit(false)}
          disabled={loading}
        >
          {loading ? 'Publishing...' : 'Publish'}
        </Button>
      </CardActions>
    </Card>
  );
};

export default KnowledgeEntryForm;
