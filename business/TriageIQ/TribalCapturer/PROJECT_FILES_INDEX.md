# Tribal Knowledge Capture Portal - Project Files Index

## Documentation Files (Root Directory)

### 📘 KNOWLEDGE_TYPES_GUIDE.md (13 KB)
**Purpose**: Comprehensive guide for all 6 knowledge types
**Contains**:
- Detailed explanation of each knowledge type
- 18+ real-world examples from database
- How AI uses each type
- Writing tips and best practices
- Testing instructions
**Audience**: MAs, Creators, System Designers

### 📗 MA_QUICK_REFERENCE.md (4 KB)
**Purpose**: Quick reference card for Medical Assistants
**Contains**:
- Quick decision tree for choosing knowledge type
- Field-by-field form guide
- Do's and don'ts
- Example entries by length
- Save vs Publish explanation
**Audience**: Medical Assistants (primary users)

### 📕 IMPLEMENTATION_GUIDE.md (25 KB)
**Purpose**: Technical implementation documentation
**Contains**:
- Architecture overview
- Database schema
- API endpoints
- Authentication flow
- Deployment instructions
**Audience**: Developers

### 📙 IMPLEMENTATION_SUMMARY.md (10 KB)
**Purpose**: High-level summary of implementation
**Contains**:
- Feature list
- Technology stack
- What was built
- Testing status
**Audience**: Project managers, stakeholders

### 📔 README.md (4 KB)
**Purpose**: Project overview and quick start
**Contains**:
- What the project does
- How to run locally
- Test credentials
- Key features
**Audience**: All users

---

## Backend Files

### 📄 backend/KNOWLEDGE_TYPE_EXAMPLES.md (9 KB)
**Purpose**: Detailed examples for each knowledge type
**Contains**:
- Free-form entry guidelines
- 3+ examples per knowledge type
- What to write for each category
- Tips for writing good entries
**Location**: `/Users/karthi/business/TriageIQ/TribalCapturer/backend/`

### 🔧 backend/seed_all_knowledge.sh (Executable)
**Purpose**: Populate database with sample entries
**Contains**:
- 18 sample knowledge entries (3 per type)
- Covers all 6 knowledge types
- Real-world examples
**Usage**: `./backend/seed_all_knowledge.sh`
**Location**: `/Users/karthi/business/TriageIQ/TribalCapturer/backend/`

---

## Database Schema

### Knowledge Entry Table Fields

| Field | Type | Purpose |
|---|---|---|
| `id` | UUID | Unique identifier |
| `user_id` | UUID | MA who created entry |
| `ma_name` | String | MA's full name |
| `facility` | String | Hospital/clinic (dropdown) |
| `specialty_service` | String | Department/specialty |
| **`provider_name`** | String | Specific doctor (optional) |
| **`knowledge_type`** | Enum | 1 of 6 categories |
| **`is_continuity_care`** | Boolean | Continuity flag |
| `knowledge_description` | Text | Free-form entry (main field) |
| `status` | Enum | draft or published |
| `created_at` | Timestamp | When created |
| `updated_at` | Timestamp | Last modified |

**Bold fields** = New intelligent fields added

---

## Knowledge Type Enum Values

```python
class KnowledgeType(str, enum.Enum):
    DIAGNOSIS_SPECIALTY = "diagnosis_specialty"      # Diagnosis → Specialty
    PROVIDER_PREFERENCE = "provider_preference"      # Provider-specific
    CONTINUITY_CARE = "continuity_care"              # Same provider rules
    PRE_VISIT_REQUIREMENT = "pre_visit_requirement"  # Pre-appointment needs
    SCHEDULING_WORKFLOW = "scheduling_workflow"      # Multi-step processes
    GENERAL_KNOWLEDGE = "general_knowledge"          # Clinic tips
```

---

## API Endpoints (Knowledge)

### Standard CRUD
- `POST /api/v1/knowledge-entries/` - Create entry (MA role)
- `GET /api/v1/knowledge-entries/{id}` - Get entry by ID
- `PUT /api/v1/knowledge-entries/{id}` - Update entry (MA, own only)
- `DELETE /api/v1/knowledge-entries/{id}` - Delete entry (MA, own only)
- `GET /api/v1/knowledge-entries/my-entries` - List MA's entries
- `GET /api/v1/knowledge-entries/` - List all published (Creator role)

### Intelligent Search
- `GET /api/v1/knowledge-entries/smart-search/` - Semantic search (OpenAI)
- `GET /api/v1/knowledge-entries/search/` - Full-text search (PostgreSQL)
- `GET /api/v1/knowledge-entries/autocomplete/{field}` - Autocomplete

### AI-Ready Endpoints
- `GET /api/v1/knowledge-entries/checklist/` - Pre-appointment checklist
- `GET /api/v1/knowledge-entries/checklist/by-diagnosis/` - Diagnosis routing

---

## Frontend Components

### Pages
- `MADashboard.tsx` - MA view (create, edit, view own entries)
- `CreatorDashboard.tsx` - Creator view (browse all, search)
- `LoginPage.tsx` - Authentication

### Components
- **`KnowledgeEntryForm.tsx`** - Form with 6 knowledge types + examples
- **`IntelligentSearch.tsx`** - Semantic search with relevance scores
- `KnowledgeList.tsx` - Paginated list view
- `KnowledgeDetail.tsx` - Modal for viewing entry details
- `FilterBar.tsx` - Filter by facility, specialty, keyword search
- `AppNavBar.tsx` - Navigation and logout

**Bold components** = Updated with intelligent features

---

## Sample Data (After Seeding)

| Knowledge Type | Count | Example |
|---|---|---|
| Diagnosis → Specialty | 3 | "Crohn's disease → Rheumatology" |
| Provider Preference | 3 | "Dr. Mitchell prefers afternoon slots" |
| Continuity of Care | 3 | "Oncology patients: same doctor" |
| Pre-Visit Requirement | 4 | "Heart failure: BNP labs within 48hrs" |
| Scheduling Workflow | 3 | "Bariatric: Auth → Nutrition → Surgeon" |
| General Knowledge | 5 | "Friday: last slots at 3 PM (lab closes)" |
| **TOTAL** | **21** | All types represented |

---

## Test Credentials

### Medical Assistants (Can Create/Edit Entries)
```
ma1@tribaliq.com / TestPassword123!
ma2@tribaliq.com / TestPassword123!
```

### Creators (Can Search/View All Entries)
```
creator1@tribaliq.com / TestPassword123!
creator2@tribaliq.com / TestPassword123!
```

---

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://tribal_user:tribal_pass@localhost:54321/tribal_knowledge_portal
JWT_SECRET=your-secret-key-min-32-characters-long-change-in-production
OPENAI_API_KEY=sk-proj-...  # For semantic search
CORS_ORIGINS=["http://localhost:5777","http://localhost:3000"]
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8777
```

---

## Local Development

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8777 --reload
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

### Access Points
- Frontend: http://localhost:5777
- Backend API Docs: http://localhost:8777/docs
- Backend Health: http://localhost:8777/health
- Database: postgresql://localhost:54321

---

## Key Features Summary

✅ **6 Knowledge Types** - Each serves different AI use case
✅ **Free-Form Entry** - No rigid templates, natural language
✅ **Semantic Search** - OpenAI embeddings (61-68% relevance)
✅ **Autocomplete** - Provider, specialty, facility suggestions
✅ **Checklist Generation** - Extracts requirements for AI
✅ **Diagnosis Routing** - Maps conditions to specialties
✅ **Provider Preferences** - Optimizes scheduling slots
✅ **Continuity Rules** - Checks patient history
✅ **Workflow Sequencing** - Multi-step appointments

---

## Files Modified in This Session

### Backend
- `src/models/knowledge_entry.py` - Added KnowledgeType enum, new fields
- `src/database/migrations/versions/002_add_provider_and_knowledge_type.py` - Migration
- `src/api/schemas/knowledge.py` - Updated Pydantic schemas
- `src/services/knowledge_service.py` - **FIXED: Added new fields to create/update**
- `src/services/semantic_search_service.py` - NEW: AI search
- `src/services/checklist_service.py` - NEW: Checklist extraction
- `src/api/routes/knowledge.py` - Added 4 new endpoints
- `src/config.py` - Added OPENAI_API_KEY
- `.env` - Added OpenAI key

### Frontend
- `src/types/index.ts` - Added KnowledgeType enum
- `src/components/KnowledgeEntryForm.tsx` - **UPDATED: Added 3 new fields + examples**
- `src/components/IntelligentSearch.tsx` - NEW: Semantic search UI
- `src/pages/CreatorDashboard.tsx` - Added tabs (Browse + Intelligent Search)

---

## What Was Fixed in Latest Update

**Issue**: New fields (`provider_name`, `knowledge_type`, `is_continuity_care`) weren't being saved

**Root Cause**: `knowledge_service.py` create/update functions didn't include new fields

**Fix Applied**:
- Updated `create_knowledge_entry()` in `src/services/knowledge_service.py:38-48`
- Updated `update_knowledge_entry()` in `src/services/knowledge_service.py:217-231`
- Now all 3 intelligent fields are saved correctly

**Verification**:
```bash
✅ Provider Name: "Dr. James Anderson" (saved correctly)
✅ Knowledge Type: "pre_visit_requirement" (saved correctly)
✅ Continuity Care: True (saved correctly)
✅ Semantic Search: 67.06% relevance (AI working!)
```

---

## Next Steps for Production

1. **Test Locally** - Use provided credentials
2. **Create Sample Data** - MAs add real tribal knowledge
3. **Test Semantic Search** - Verify OpenAI integration
4. **Deploy to Railway** - HTTPS will fix secure cookie issue
5. **Update Environment** - Add production DATABASE_URL, OPENAI_API_KEY
6. **Re-run Migrations** - `alembic upgrade head` on production
7. **Seed Sample Data** - Run `./seed_all_knowledge.sh` (optional)
8. **Test End-to-End** - Verify all 6 knowledge types work

---

*Last Updated: December 17, 2025*
*Total Entries: 21 published*
*All 6 Knowledge Types: Implemented and Tested*
