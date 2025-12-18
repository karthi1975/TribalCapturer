# Tribal Knowledge Types - MA Entry Guide

## Overview

The Intelligent Tribal Knowledge Capture Portal supports **6 knowledge types**. Each type helps AI understand and use the knowledge for automated scheduling and triage decisions.

MAs can enter **free-form text** for any type - the examples below are guidelines, not rigid templates.

---

## ✅ Database Status (Current)

| Knowledge Type | Count | With Provider | Continuity Care |
|---|---|---|---|
| **Diagnosis → Specialty** | 3 | 3 | 0 |
| **Provider Preference** | 3 | 3 | 0 |
| **Continuity of Care** | 3 | 3 | 3 |
| **Pre-Visit Requirement** | 4 | 4 | 1 |
| **Scheduling Workflow** | 3 | 3 | 0 |
| **General Knowledge** | 5 | 3 | 0 |
| **TOTAL** | **21** | **19** | **4** |

---

## 1. 📋 Diagnosis → Specialty Referral

**Purpose**: Maps patient diagnoses/conditions to appropriate specialties for AI routing

**When to use**:
- Patient has specific diagnosis that requires specialist
- Certain conditions need specific departments
- Prerequisites exist before scheduling specialty

**Free-form entry tips**:
- Mention the diagnosis/condition clearly
- State which specialty to schedule
- Include any prerequisites (e.g., "check if GI consult done first")
- Note urgency if relevant

**Examples**:

```
Patient with new diagnosis of Crohn's disease needs appointment with
Rheumatologist. Important: Check if GI consult has been completed first -
many rheumatologists want GI evaluation done before starting rheumatology
care. If no GI consult, schedule GI first, then rheumatology 2-4 weeks later.
```

```
New MI (myocardial infarction) patients need Cardiology follow-up within
2 weeks of hospital discharge. Schedule stress test for 4-6 weeks post-MI
if ordered by cardiologist. Mark as urgent priority when scheduling.
```

```
Hypothyroid patients with TSH levels >10 need Endocrinology referral. If TSH
is between 5-10, PCP can manage unless patient has severe symptoms or is
pregnant. Always check most recent TSH before scheduling endo.
```

**AI Use**: Routes diagnoses to correct specialty, checks prerequisites

---

## 2. 👨‍⚕️ Provider Preference

**Purpose**: Documents specific provider scheduling preferences and requirements

**When to use**:
- Provider has specific scheduling preferences (morning/afternoon)
- Provider requires specific preparations
- Provider has day-of-week restrictions
- Provider needs specific appointment duration for certain cases

**Free-form entry tips**:
- ALWAYS fill in the "Provider Name" field for this type
- Explain the preference and WHY it exists
- Include consequences if preference not followed
- Mention any time/day restrictions

**Examples**:

```
Dr. Mitchell prefers new patients in afternoon slots (after 1 PM) because
she reviews charts in the morning. Complex cardiac cases need 60-minute
appointments, not standard 30-minute slots. She also requires recent EKG
results uploaded before the appointment.
```

```
Dr. Martinez only sees pediatric cardiology patients on Tuesdays and
Thursdays. Don't schedule pediatric patients on other days even if calendar
shows availability - those slots are for adult patients. All pediatric echo
studies should be scheduled same day as appointment when possible.
```

```
Dr. Johnson requires all diabetic patients to bring glucose logs from past
2 weeks to appointment. She will reschedule if patient doesn't have logs -
it saves everyone's time to remind patients when scheduling. Also ask
patients to bring all current medications in original bottles.
```

**AI Use**: Suggests optimal time slots, prevents invalid bookings, reminds about requirements

---

## 3. 🔄 Continuity of Care Rule

**Purpose**: Defines when patients MUST or SHOULD see the same provider again

**When to use**:
- Certain specialties require seeing same doctor
- Post-procedure follow-ups need original provider
- Patient outcomes improve with provider consistency
- There are exceptions to the rule

**Free-form entry tips**:
- CHECK the "Continuity of Care" checkbox for this type!
- Use words like "MUST", "SHOULD", "ALWAYS" to indicate priority
- Explain WHY continuity matters for this case
- Note any exceptions (e.g., "unless on extended leave")

**Examples**:

```
Oncology patients should ALWAYS be scheduled with their original oncologist
unless that doctor specifically transfers care. Don't just grab any open slot
with available oncologist - cancer patients need consistency and their doctor
knows their full history. Check patient history before scheduling.
```

```
Post-surgical follow-ups MUST be with the surgeon who performed the procedure.
System should block scheduling with different surgeon in same specialty. Only
exception is if the original surgeon is on extended leave - then schedule with
covering surgeon and note the reason.
```

```
Mental health patients benefit greatly from seeing the same therapist. Always
check patient history and offer their previous provider's available slots
first. However, patient CAN choose a different provider if they prefer -
don't force continuity, just prioritize it.
```

**AI Use**: Checks patient history, prioritizes previous provider's slots, warns if different provider selected

---

## 4. 🧪 Pre-Visit Requirement

**Purpose**: What patients need to do/bring BEFORE the appointment

**When to use**:
- Lab work required (with timing)
- Imaging needed
- Patient preparation (fasting, NPO, etc.)
- Documents/records to bring
- Photos or logs required

**Free-form entry tips**:
- Be SPECIFIC about timing (e.g., "within 48 hours")
- List requirements with numbers (1), (2), (3)
- Mention consequences if requirements not met
- Include both required and recommended items

**Examples**:

```
Heart failure follow-up appointments require: (1) BNP labs drawn within 48
hours before appointment, (2) Current weight recorded, (3) BP log from home
monitoring if patient has blood pressure cuff. If morning appointment and
labs needed, patient should be NPO after midnight. Dr. Mitchell will not see
patient without recent BNP levels.
```

```
New dermatology patients coming for mole check should: (1) Take photos of
concerning spots before visit, (2) Bring list of ALL current medications
including supplements, (3) Wear clothing that allows easy access to areas
of concern. Parents of pediatric patients should document when moles first
appeared.
```

```
New rheumatology patients MUST have these labs drawn at least 3 days before
appointment: CBC, CMP, ESR, CRP, RF (Rheumatoid Factor), and anti-CCP.
Dr. Anderson will NOT see new patients without these labs - appointment will
be rescheduled. Established patients don't need pre-visit labs unless
specifically ordered.
```

**AI Use**: Generates patient checklist, sends reminder messages, validates readiness before appointment

---

## 5. 📋 Scheduling Workflow

**Purpose**: Multi-step processes and coordination requirements

**When to use**:
- Appointment requires multiple steps in sequence
- Need to coordinate across departments
- Insurance authorization required
- Specific order of operations matters

**Free-form entry tips**:
- Number the steps clearly: (1), (2), (3)
- Explain WHY steps must be in this order
- Include timing between steps if relevant
- Mention any parallel processes ("can happen concurrently")

**Examples**:

```
Bariatric surgery consult workflow: (1) First verify insurance pre-authorization
is approved, (2) Schedule nutrition consult FIRST - this is mandatory, (3) Then
schedule surgeon consult 2-4 weeks after nutrition appointment, (4) Psychology
evaluation can happen concurrently with surgeon consult. Don't schedule surgeon
before nutrition - it's a waste of everyone's time and surgeon won't proceed
without nutrition clearance.
```

```
Orthopedic post-op follow-up workflow: Check if physical therapy (PT) was
ordered. If yes, try to coordinate PT and surgeon follow-up appointments on
the same day when possible - patients love one-stop visits and surgeon wants
PT progress feedback during the visit. Schedule PT about 30 minutes before
surgeon so therapist can give update.
```

```
Sleep study scheduling workflow: (1) Verify sleep medicine referral is in
system, (2) Submit insurance authorization request (takes 3-5 business days),
(3) Once approved, call patient to explain home study vs lab study options,
(4) Schedule the sleep study, (5) Automatically schedule follow-up appointment
2 weeks after study date for results review with sleep doctor.
```

**AI Use**: Sequences multi-step appointments automatically, checks prerequisites, coordinates timing

---

## 6. 💡 General Knowledge

**Purpose**: Clinic operations, tips, and knowledge that doesn't fit other categories

**When to use**:
- Clinic-specific quirks or limitations
- Operational hours or restrictions
- Helpful tips for patients or staff
- Cross-facility coordination
- Special services (interpreters, parking, etc.)

**Free-form entry tips**:
- Write like teaching a new MA teammate
- Explain the "why" behind the rule
- Include consequences or patient impact
- Note any exceptions

**Examples**:

```
Friday afternoon scheduling: Last appointment slots should be 3 PM because
the lab closes at 4 PM and many patients need bloodwork drawn after their
visit. Don't schedule 4 PM or later slots on Fridays even if the system
allows it - patients get frustrated when they can't get labs done.
```

```
Interpreter services scheduling: Need 48-hour advance notice for ASL (sign
language) interpreters, 24-hour notice for Spanish interpreters. Video remote
interpreting is available same-day for other languages. Always note language
needs in appointment comments when scheduling so interpreter is ready when
patient arrives.
```

```
Parking validation: We only validate parking for appointments lasting over
1 hour. Tell patients during scheduling if they'll need to pay for parking
so they can bring cash or card. Validation desk is on first floor near main
entrance - direct patients there after long appointments.
```

**AI Use**: Prevents common mistakes, improves patient communication, optimizes scheduling

---

## How AI Uses This Knowledge

| Knowledge Type | AI Capability |
|---|---|
| **Diagnosis → Specialty** | Auto-routes patient to correct department, checks prerequisites |
| **Provider Preference** | Suggests optimal appointment slots, validates requirements |
| **Continuity of Care** | Searches patient history, prioritizes previous provider |
| **Pre-Visit Requirement** | Generates checklist, sends reminders, validates readiness |
| **Scheduling Workflow** | Sequences multi-step appointments, coordinates departments |
| **General Knowledge** | Prevents errors, improves patient experience |

---

## Tips for Writing Good Free-Form Entries

1. **Be Specific**: Include exact timing, dosages, requirements
   - ❌ "Patient needs labs before appointment"
   - ✅ "BNP labs must be drawn within 48 hours before appointment"

2. **Explain WHY**: Helps AI and humans understand reasoning
   - ❌ "Dr. Smith prefers afternoon"
   - ✅ "Dr. Smith prefers afternoon slots because she reviews charts in morning"

3. **Include Consequences**: Shows priority level
   - ❌ "Bring glucose logs"
   - ✅ "Bring glucose logs or appointment will be rescheduled"

4. **Use Examples**: Makes it concrete
   - ❌ "Some conditions need rheumatology"
   - ✅ "Crohn's disease needs Rheumatologist - check GI consult first"

5. **Write Conversationally**: Like teaching a colleague
   - ❌ "Authorization required pre-scheduling"
   - ✅ "First verify insurance pre-auth is approved before scheduling"

6. **Note Exceptions**: Prevents overgeneralization
   - ❌ "Always same surgeon"
   - ✅ "Same surgeon unless on extended leave - then use covering surgeon"

---

## Testing Your Entry

After submitting, Creators can test if AI understands your entry:

**Semantic Search**: Try natural language queries
- "What do I need for heart failure appointment?"
- "Which specialty for Crohn's disease?"
- "Can I schedule Dr. Martinez on Monday?"

**Autocomplete**: Verify your entry appears in suggestions
- Type provider name → Should autocomplete
- Type specialty → Should show in dropdown
- Type facility → Should suggest

**Checklist**: See if AI extracts requirements correctly
- Filter by specialty + provider
- Check if your entry appears in checklist

---

## Questions?

- Login as **MA** to create entries (ma1@tribaliq.com / TestPassword123!)
- Login as **Creator** to search and test (creator1@tribaliq.com / TestPassword123!)
- All 6 knowledge types accept **free-form text** - no rigid templates!
- AI learns from your writing style and improves over time

---

*Last updated: December 2025*
*Knowledge entries: 21 published*
*Semantic search powered by: OpenAI text-embedding-3-small*
