
	I think for harvesting tribal knowledge and to maintain an ongoing iterative system I’d like to have an online database that caregivers will have access to. They could log onto the database select their clinic and provider then enter free text that we could evaluate and integrate into the AI scheduling system. What do you think of that idea?


	Good idea, I will create a public facing site that captures the details and let you know.,

	In the demo I noticed that we were entering free text of symptoms. The system will likely be scheduling off of diagnosis as well. Your doc may discover that you have Chrons disease and want to schedule you to see a Rheumatologist. I assume the system will be able to handle that as well? So the prompt maybe “pt has new diagnosis of Chrons disease needs an appointment with a Rheumatologist “ 
	Another huge feature needs to be checking if the patient has already seen someone in that specialty, and give preference to see that doc again. Perhaps I have seen a cardiologist in the past and I need to go back the system should recommend I see the same provider for continuity of care purposes. Obviously the patient could decline that provider but the system needs to recognize they have seen someone before in that specialty and recommend that same physicians slots. 
---

## Deep Dive: Tribal Knowledge Capture System

### The Core Problem

Tribal knowledge in healthcare scheduling exists in multiple forms:
- **Explicit** ("Dr. Patel doesn't see new patients on Fridays")
- **Implicit** (schedulers unconsciously avoid booking complex cases at 4pm)
- **Contextual** ("If the patient mentions anxiety, give them the first appointment of the day")
- **Relational** ("When referring from Dr. A to Dr. B, always call ahead")
- **Temporal** ("January is heavy for depression follow-ups")

A simple form captures only explicit knowledge. You need a multi-channel approach.

---

### Channel 1: Direct Knowledge Entry Portal (Primary)

**Who uses it:** Schedulers, clinic managers, providers, care coordinators

**Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  TRIBAL KNOWLEDGE CAPTURE PORTAL                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  YOUR INFO                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Clinic ▼        │  │ Your Role ▼     │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                             │
│  THIS KNOWLEDGE IS ABOUT                                    │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Provider ▼      │  │ All Providers   │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                             │
│  CATEGORY (select all that apply)                          │
│  ☐ Scheduling Preferences    ☐ Patient Type Handling       │
│  ☐ Diagnosis/Referral Rules  ☐ Timing/Duration Rules       │
│  ☐ Insurance/Auth Quirks     ☐ Communication Preferences   │
│  ☐ Exception/Edge Case       ☐ Continuity of Care Rule     │
│                                                             │
│  TELL US WHAT YOU KNOW                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ "When scheduling a new autism eval for Dr. Chen,    │   │
│  │  always book 90 minutes and avoid Mondays - she     │   │
│  │  does home visits then. If the family speaks        │   │
│  │  Spanish, try to book Maria as the interpreter..."  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  HOW CERTAIN IS THIS?                                       │
│  ○ Official policy  ○ Strongly preferred  ○ Soft rule      │
│                                                             │
│  WHAT HAPPENS IF WE IGNORE THIS?                           │
│  ○ Major problem  ○ Inefficiency  ○ Minor annoyance        │
│                                                             │
│                              [Submit Knowledge]             │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- Free text is primary (don't over-structure or you'll lose nuance)
- Categories help with downstream processing but aren't restrictive
- Severity/certainty helps prioritize rule integration
- Role capture helps weight reliability (scheduler vs. new hire)

---

### Channel 2: Prompted Knowledge Mining (Structured Interviews)

**Problem:** People don't know what they know until prompted.

**Solution:** Periodic guided questionnaires that probe specific scenarios:

```
SCENARIO-BASED KNOWLEDGE EXTRACTION

Scenario 1: A patient with newly diagnosed Type 2 Diabetes needs 
to establish care with Endocrinology.

- What questions would you ask before scheduling?
- Which provider would you recommend? Why?
- What time of day works best for this visit type?
- How long should the appointment be?
- What should happen before this visit?
- What commonly goes wrong with this type of scheduling?

Scenario 2: A child with developmental delays needs a 
multidisciplinary evaluation.

[Same prompting structure]
```

**Implementation:** Monthly "knowledge harvest" sessions—15 minutes, rotating scenarios, small incentive for participation.

---

### Channel 3: Friction Point Capture (Real-Time)

**Problem:** Best knowledge emerges when something goes wrong.

**Solution:** A "quick capture" mechanism embedded in the scheduling workflow:

```
┌────────────────────────────────────────┐
│ 🚨 LOG A SCHEDULING FRICTION POINT    │
├────────────────────────────────────────┤
│ What just happened?                    │
│ ┌────────────────────────────────────┐ │
│ │ Patient showed up but provider was │ │
│ │ actually at the other clinic...    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ What should the system have known?     │
│ ┌────────────────────────────────────┐ │
│ │ Dr. Martinez is at Clinic B on     │ │
│ │ 2nd Thursdays of the month         │ │
│ └────────────────────────────────────┘ │
│                                        │
│ [Submit]  [This was a one-time thing] │
└────────────────────────────────────────┘
```

**Trigger points:**
- Reschedules
- No-shows
- Patient complaints
- Provider complaints
- Long hold times
- Same-day cancellations

---

### Channel 4: Historical Pattern Mining (Passive)

**Problem:** Implicit knowledge is encoded in years of scheduling decisions.

**Solution:** Analyze historical scheduling data for hidden patterns:

```python
# Pattern Mining Queries

# 1. Provider preference patterns
SELECT provider_id, day_of_week, hour, 
       COUNT(*) as bookings,
       AVG(no_show_rate) as no_show_rate
FROM appointments
GROUP BY provider_id, day_of_week, hour
# Reveals: "Dr. Smith's Tuesday 2pm slots have 3x no-show rate"

# 2. Diagnosis → Specialty routing patterns
SELECT referring_diagnosis, 
       receiving_specialty,
       COUNT(*) as frequency,
       AVG(days_to_appointment) as avg_wait
FROM referrals
GROUP BY referring_diagnosis, receiving_specialty
# Reveals: "Crohn's patients are sent to GI 80% of time, Rheum 20%"

# 3. Continuity of care patterns
SELECT patient_id, specialty, 
       COUNT(DISTINCT provider_id) as provider_count,
       MAX(CASE WHEN saw_same_provider THEN 1 ELSE 0 END) as continuity
FROM encounters
GROUP BY patient_id, specialty
# Reveals: "Patients who see same provider have 40% better show rate"

# 4. Appointment duration accuracy
SELECT visit_type, scheduled_duration, 
       AVG(actual_duration) as actual_avg,
       STDDEV(actual_duration) as variance
FROM appointments
WHERE actual_duration IS NOT NULL
GROUP BY visit_type, scheduled_duration
# Reveals: "New autism evals scheduled for 60min actually take 87min"
```

**Output:** Auto-generated rule candidates for human review.

---

### Channel 5: Feedback Loop from AI Decisions

**Problem:** You don't know if captured knowledge is working.

**Solution:** Track AI scheduling recommendations against outcomes:

```
┌─────────────────────────────────────────────────────────────┐
│ AI RECOMMENDATION FEEDBACK                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The AI recommended: Dr. Chen, Tuesday 10am                  │
│                                                             │
│ What did you actually schedule?                             │
│ ○ Accepted AI recommendation                                │
│ ○ Same provider, different time                            │
│ ○ Different provider, same time                            │
│ ○ Completely different                                      │
│                                                             │
│ If different, why? (optional)                              │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Patient requested afternoon due to work schedule    │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**This creates a continuous learning loop:**
- AI makes recommendation based on current knowledge
- Human accepts or overrides
- Override reasons become new knowledge candidates
- System improves over time

---

### Knowledge Processing Pipeline

```
                    ┌─────────────────┐
                    │  RAW KNOWLEDGE  │
                    │    ENTRIES      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  NLP EXTRACTION │
                    │  - Entities     │
                    │  - Conditions   │
                    │  - Actions      │
                    │  - Constraints  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ RULE CANDIDATE  │
                    │   GENERATION    │
                    │                 │
                    │ IF [condition]  │
                    │ THEN [action]   │
                    │ WEIGHT [score]  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  HUMAN REVIEW   │
                    │   DASHBOARD     │
                    │                 │
                    │ ✓ Approve       │
                    │ ✗ Reject        │
                    │ ✎ Modify        │
                    └────────┬────────┘
                             │
                             ▼
          ┌──────────────────┴──────────────────┐
          │                                     │
          ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│  RULE ENGINE    │                   │  RAG KNOWLEDGE  │
│  (Hard Rules)   │                   │  BASE (Soft     │
│                 │                   │   Guidance)     │
│ - Must follow   │                   │                 │
│ - System blocks │                   │ - Suggestions   │
│   violations    │                   │ - Context for   │
│                 │                   │   AI reasoning  │
└─────────────────┘                   └─────────────────┘
```

---

### Data Model (Comprehensive)

```sql
-- Core entities
CREATE TABLE clinics (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    timezone VARCHAR(50),
    specialties JSONB,
    operating_hours JSONB
);

CREATE TABLE providers (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    credentials VARCHAR(100),
    specialties JSONB,
    clinic_affiliations JSONB,  -- Can work at multiple clinics
    scheduling_preferences JSONB,
    active BOOLEAN DEFAULT true
);

-- Knowledge capture
CREATE TABLE knowledge_entries (
    id UUID PRIMARY KEY,
    submitted_by UUID REFERENCES users(id),
    submitted_at TIMESTAMP DEFAULT NOW(),
    
    -- Context
    clinic_id UUID REFERENCES clinics(id),
    provider_id UUID REFERENCES providers(id),  -- NULL if applies to all
    
    -- Classification
    categories TEXT[],  -- Array of category tags
    certainty VARCHAR(50),  -- official, preferred, soft_rule
    severity VARCHAR(50),   -- major, moderate, minor
    
    -- Content
    raw_text TEXT NOT NULL,
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processed, rejected
    processed_at TIMESTAMP,
    processed_by UUID
);

-- Extracted rules (from NLP processing)
CREATE TABLE rule_candidates (
    id UUID PRIMARY KEY,
    source_entry_id UUID REFERENCES knowledge_entries(id),
    
    -- Rule structure
    rule_type VARCHAR(100),
    conditions JSONB,    -- {"diagnosis": "Crohn's", "patient_type": "new"}
    actions JSONB,       -- {"recommend_specialty": "GI", "duration": 60}
    constraints JSONB,   -- {"avoid_days": ["Monday"], "prefer_time": "morning"}
    
    -- Scoring
    confidence_score FLOAT,
    supporting_evidence INT,  -- How many entries support this
    
    -- Review status
    status VARCHAR(50) DEFAULT 'candidate',
    reviewed_by UUID,
    reviewed_at TIMESTAMP,
    review_notes TEXT
);

-- Active rules (approved and in use)
CREATE TABLE scheduling_rules (
    id UUID PRIMARY KEY,
    source_candidate_id UUID REFERENCES rule_candidates(id),
    
    rule_type VARCHAR(100),
    conditions JSONB,
    actions JSONB,
    constraints JSONB,
    
    priority INT,  -- For conflict resolution
    is_hard_rule BOOLEAN DEFAULT false,  -- Hard = must follow, Soft = suggestion
    
    effective_from TIMESTAMP,
    effective_until TIMESTAMP,  -- NULL = no expiration
    
    -- Performance tracking
    times_applied INT DEFAULT 0,
    times_overridden INT DEFAULT 0,
    last_applied TIMESTAMP
);

-- Continuity of care tracking
CREATE TABLE patient_provider_relationships (
    patient_id UUID,
    provider_id UUID REFERENCES providers(id),
    specialty VARCHAR(100),
    
    first_encounter DATE,
    last_encounter DATE,
    encounter_count INT,
    relationship_strength FLOAT,  -- Calculated score
    
    PRIMARY KEY (patient_id, provider_id, specialty)
);

-- Feedback loop
CREATE TABLE scheduling_feedback (
    id UUID PRIMARY KEY,
    recommendation_id UUID,  -- Links to AI recommendation
    
    ai_recommended_provider UUID,
    ai_recommended_time TIMESTAMP,
    
    actual_provider UUID,
    actual_time TIMESTAMP,
    
    accepted BOOLEAN,
    override_reason TEXT,
    
    -- Outcome tracking
    patient_showed BOOLEAN,
    appointment_completed BOOLEAN,
    duration_accuracy FLOAT,  -- Actual / Scheduled
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Friction point captures
CREATE TABLE friction_reports (
    id UUID PRIMARY KEY,
    reported_by UUID,
    reported_at TIMESTAMP DEFAULT NOW(),
    
    appointment_id UUID,
    friction_type VARCHAR(100),
    
    what_happened TEXT,
    what_system_should_know TEXT,
    
    was_one_time BOOLEAN DEFAULT false,
    
    status VARCHAR(50) DEFAULT 'new',
    converted_to_knowledge_entry UUID REFERENCES knowledge_entries(id)
);
```

---

### The Continuity of Care Feature (Deep Dive)

This deserves special attention since you called it out:

```
CONTINUITY OF CARE LOGIC

1. TRIGGER: New referral/appointment request for specialty X

2. QUERY: Has patient seen anyone in specialty X before?
   
   SELECT provider_id, provider_name, 
          encounter_count, last_encounter,
          relationship_strength
   FROM patient_provider_relationships
   WHERE patient_id = [current_patient]
     AND specialty = [requested_specialty]
   ORDER BY relationship_strength DESC

3. IF previous provider exists:
   
   ┌─────────────────────────────────────────────────────────┐
   │ CONTINUITY OF CARE RECOMMENDATION                       │
   ├─────────────────────────────────────────────────────────┤
   │                                                         │
   │ Patient has previously seen:                            │
   │                                                         │
   │ ⭐ Dr. Sarah Martinez (Cardiology)                      │
   │    Last visit: 3 months ago                             │
   │    Total visits: 7                                      │
   │    Relationship strength: Strong                        │
   │                                                         │
   │    Next available: Tuesday, Jan 14 at 2:00 PM          │
   │    [Book with Dr. Martinez]                             │
   │                                                         │
   │ ─────────────────────────────────────────────────────── │
   │                                                         │
   │ Or choose a different provider:                         │
   │    Dr. James Liu - Available tomorrow                   │
   │    Dr. Patricia Wong - Available Friday                 │
   │                                                         │
   │ Patient declines previous provider? [Log reason]        │
   │                                                         │
   └─────────────────────────────────────────────────────────┘

4. RELATIONSHIP STRENGTH CALCULATION:
   
   score = (
       encounter_count * 0.3 +
       recency_score * 0.3 +      # Higher if recent
       visit_consistency * 0.2 +   # Regular intervals = stronger
       complexity_score * 0.2      # Complex cases = stronger bond
   )

5. EXCEPTIONS TO CONTINUITY:
   - Provider no longer at organization
   - Provider not accepting patients
   - Patient explicitly declined
   - Urgency requires sooner appointment
   - Insurance change breaks network
```

---

### Diagnosis-Based Routing

```
DIAGNOSIS → SPECIALTY MAPPING

1. STRUCTURED MAPPINGS (ICD-10 based):
   
   CREATE TABLE diagnosis_specialty_routing (
       icd10_code VARCHAR(10),
       icd10_description TEXT,
       primary_specialty VARCHAR(100),
       secondary_specialty VARCHAR(100),
       requires_referral BOOLEAN,
       typical_urgency VARCHAR(50),
       notes TEXT
   );
   
   Examples:
   K50.* (Crohn's) → GI (primary), Rheumatology (secondary if joint involvement)
   E11.* (Type 2 DM) → Endocrinology (primary), Nutrition (secondary)
   F32.* (Depression) → Psychiatry (primary), Psychology (secondary)

2. NLP EXTRACTION from free text:
   
   Input: "pt has new diagnosis of Crohn's disease needs 
           appointment with Rheumatologist"
   
   Extracted:
   - Diagnosis: Crohn's disease (K50.9)
   - Requested specialty: Rheumatology
   - Patient type: Likely new to specialty
   - Urgency: Standard (no urgency markers)
   
3. ROUTING LOGIC:
   
   IF extracted_specialty matches diagnosis_routing:
       → Proceed with requested specialty
   ELSE:
       → Flag for review: "Crohn's typically routes to GI first. 
          Rheumatology requested. Confirm?"
   
   IF diagnosis has prerequisite specialty:
       → Check if patient has completed it
       → If not: "Patient may need GI evaluation before Rheumatology"
```

---

### Implementation Phases

**Phase 1: Foundation (Weeks 1-2)**
- Deploy basic knowledge entry portal
- Set up database schema
- Basic authentication (clinic/role-based)
- Simple submission workflow

**Phase 2: Processing (Weeks 3-4)**
- NLP extraction pipeline (GPT-based)
- Rule candidate generation
- Admin review dashboard
- Basic rule engine integration

**Phase 3: Intelligence (Weeks 5-6)**
- Continuity of care queries (FHIR integration)
- Diagnosis routing logic
- Historical pattern mining scripts
- Feedback loop mechanism

**Phase 4: Optimization (Ongoing)**
- Performance dashboards
- Rule effectiveness tracking
- Continuous knowledge harvesting
- Model refinement based on outcomes
