# Knowledge Type Examples for MAs

## Free-Form Entry Guidelines by Knowledge Type

Each knowledge type serves a specific purpose for AI scheduling. Here's what MAs should document in the free-form description field:

---

## 1. Diagnosis → Specialty Referral

**Purpose**: Maps patient diagnoses to the appropriate specialty for scheduling

**What to write**:
- What diagnosis/condition requires which specialty
- If there are prerequisites before scheduling
- Urgency level for certain conditions

**Examples**:

```
Patient with new diagnosis of Crohn's disease needs appointment with Rheumatologist.
Note: Check if GI consult completed first - many doctors want GI evaluation before
rheumatology referral.
```

```
New MI (myocardial infarction) patients need Cardiology follow-up within 2 weeks of
hospital discharge. Schedule stress test for 4-6 weeks post-MI if ordered.
```

```
Hypothyroid patients with TSH >10 need Endocrinology referral. If TSH 5-10, PCP can
manage unless symptoms severe.
```

---

## 2. Provider Preference

**Purpose**: Documents specific provider preferences and requirements

**What to write**:
- Provider's scheduling preferences (morning/afternoon)
- How provider likes appointments structured
- Provider-specific preparation requirements
- Communication preferences

**Examples**:

```
Dr. Smith prefers new patients in afternoon slots (after 1 PM) because she reviews
charts in the morning. Complex cases need 60-minute appointments, not standard 30.
```

```
Dr. Johnson requires all diabetic patients to bring glucose logs from past 2 weeks.
She will reschedule if patient doesn't have logs - saves everyone time to check first.
```

```
Dr. Martinez only sees pediatric cardiology on Tuesdays and Thursdays. Don't schedule
peds patients on other days even if slot shows open - those are adult-only days.
```

---

## 3. Continuity of Care Rule

**Purpose**: When patients MUST or SHOULD see the same provider again

**What to write**:
- Which conditions require same-provider continuity
- When to prioritize returning to previous provider
- Exceptions to continuity rules

**Examples**:

```
Oncology patients should ALWAYS be scheduled with their original oncologist unless
that doctor specifically transfers care. Don't just grab any open slot - cancer
patients need consistency.
```

```
Post-surgical follow-ups MUST be with the surgeon who performed the procedure. System
should block scheduling with different surgeon in same specialty.
```

```
Mental health patients benefit from seeing same therapist. Check history and offer
their previous provider's slots first, but patient can choose different provider if
they prefer.
```

---

## 4. Pre-Visit Requirement

**Purpose**: What patients need to do/bring BEFORE the appointment

**What to write**:
- Lab work required (and timing)
- Imaging needed
- Paperwork/records to bring
- Fasting or preparation instructions
- Medication requirements

**Examples**:

```
Heart failure follow-ups: BNP labs must be drawn within 48 hours before appointment.
Also need current weight, BP log from home monitoring if patient has cuff. NPO after
midnight if AM appointment and labs needed.
```

```
New dermatology patients for mole check: Take photos of concerning spots before visit.
Bring list of all current medications including supplements. Wear clothing that allows
easy access to areas of concern.
```

```
Rheumatology new patients: Need CBC, CMP, ESR, CRP, RF, anti-CCP drawn at least 3 days
before appointment. Dr. Anderson won't see new patients without these labs - will
reschedule.
```

---

## 5. Scheduling Workflow

**Purpose**: Step-by-step process tips and best practices

**What to write**:
- Sequence of steps for complex scheduling
- Workarounds for common issues
- Cross-department coordination needs
- Authorization/referral requirements

**Examples**:

```
For bariatric surgery consults: (1) Verify insurance pre-auth approved, (2) Schedule
nutrition consult FIRST, (3) Then schedule surgeon consult 2-4 weeks after nutrition,
(4) Psychology eval can be concurrent with surgeon. Don't schedule surgeon before
nutrition - waste of everyone's time.
```

```
Orthopedic surgery follow-up workflow: Check if PT ordered. If yes, coordinate PT and
surgeon follow-up on same day when possible - patients love one-stop appointments and
surgeon wants PT feedback during visit.
```

```
When scheduling Sleep Study: (1) Verify sleep medicine referral, (2) Get insurance
auth (takes 3-5 days), (3) Call patient to explain home vs lab study options, (4)
Schedule study, (5) Auto-schedule follow-up 2 weeks after study for results review.
```

---

## 6. General Knowledge

**Purpose**: Tribal knowledge that doesn't fit other categories

**What to write**:
- Clinic-specific quirks
- Helpful tips for patients
- Coordination with other facilities
- Special circumstances

**Examples**:

```
Friday afternoon appointments: Last appointments are 3 PM because lab closes at 4 PM
and patients often need bloodwork after visit. Don't schedule 4 PM slots even if
system allows.
```

```
Interpreter services: Need 48-hour notice for ASL interpreters, 24-hour notice for
Spanish. Video interpreting available same-day for other languages. Note language need
in appointment notes.
```

```
Parking validation: We only validate for appointments over 1 hour. Tell patients at
scheduling if they need to pay for parking so they bring cash/card.
```

---

## Tips for Writing Good Free-Form Entries:

1. **Be Specific**: Include timing, dosages, exact requirements
2. **Explain WHY**: Helps AI and humans understand the reasoning
3. **Use Examples**: "Dr. Smith needs X" is clearer than "providers need X"
4. **Include Consequences**: "...or appointment will be rescheduled" helps prioritize
5. **Write Conversationally**: Like teaching a new MA teammate
6. **Note Exceptions**: "Usually X, but if Y then Z"

---

## What AI Scheduling System Does With This Knowledge:

- **Diagnosis → Specialty**: Routes patient to correct department automatically
- **Provider Preference**: Suggests optimal time slots and appointment types
- **Continuity of Care**: Checks history and prioritizes previous provider
- **Pre-Visit Requirements**: Generates checklist for patient AND scheduler
- **Scheduling Workflow**: Sequences multi-step appointments automatically
- **General Knowledge**: Prevents common mistakes and improves patient experience
