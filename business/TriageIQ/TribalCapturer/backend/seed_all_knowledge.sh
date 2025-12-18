#!/bin/bash

echo "======================================================================"
echo "🌱 Seeding Knowledge Base with All 6 Knowledge Types"
echo "======================================================================"

# Login as MA
echo ""
echo "🔐 Logging in as MA..."
curl -s -X POST http://localhost:8777/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ma1@tribaliq.com","password":"TestPassword123!"}' \
  -c /tmp/seed_cookies.txt > /dev/null

echo "✅ Login successful"
echo ""
echo "📝 Creating 18 knowledge entries across all 6 types..."
echo ""

# Counter
COUNT=0

# DIAGNOSIS → SPECIALTY (3 entries)
echo "📋 DIAGNOSIS → SPECIALTY"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Rheumatology",
    "provider_name": "",
    "knowledge_type": "diagnosis_specialty",
    "is_continuity_care": false,
    "knowledge_description": "Patient with new diagnosis of Crohns disease needs appointment with Rheumatologist. Important: Check if GI consult has been completed first - many rheumatologists want GI evaluation done before starting rheumatology care. If no GI consult, schedule GI first, then rheumatology 2-4 weeks later.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Crohns → Rheumatology"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Cardiology",
    "provider_name": "",
    "knowledge_type": "diagnosis_specialty",
    "is_continuity_care": false,
    "knowledge_description": "New MI (myocardial infarction) patients need Cardiology follow-up within 2 weeks of hospital discharge. Schedule stress test for 4-6 weeks post-MI if ordered by cardiologist. Mark as urgent priority when scheduling.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] MI → Cardiology"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Utah Valley Hospital – Provo, UT",
    "specialty_service": "Endocrinology",
    "provider_name": "",
    "knowledge_type": "diagnosis_specialty",
    "is_continuity_care": false,
    "knowledge_description": "Hypothyroid patients with TSH levels >10 need Endocrinology referral. If TSH is between 5-10, PCP can manage unless patient has severe symptoms or is pregnant. Always check most recent TSH before scheduling endo.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Hypothyroid → Endocrinology"

echo ""
echo "👨‍⚕️ PROVIDER PREFERENCE"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Cardiology",
    "provider_name": "Dr. Sarah Mitchell",
    "knowledge_type": "provider_preference",
    "is_continuity_care": false,
    "knowledge_description": "Dr. Mitchell prefers new patients in afternoon slots (after 1 PM) because she reviews charts in the morning. Complex cardiac cases need 60-minute appointments, not standard 30-minute slots. She also requires recent EKG results uploaded before the appointment.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Dr. Mitchell - Cardiology"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Primary Childrens Hospital – Salt Lake City, UT",
    "specialty_service": "Pediatric Cardiology",
    "provider_name": "Dr. Martinez",
    "knowledge_type": "provider_preference",
    "is_continuity_care": false,
    "knowledge_description": "Dr. Martinez only sees pediatric cardiology patients on Tuesdays and Thursdays. Dont schedule pediatric patients on other days even if calendar shows availability - those slots are for adult patients. All pediatric echo studies should be scheduled same day as appointment when possible.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Dr. Martinez - Pediatric Cardiology"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "LDS Hospital – Salt Lake City, UT",
    "specialty_service": "Endocrinology",
    "provider_name": "Dr. Johnson",
    "knowledge_type": "provider_preference",
    "is_continuity_care": false,
    "knowledge_description": "Dr. Johnson requires all diabetic patients to bring glucose logs from past 2 weeks to appointment. She will reschedule if patient doesnt have logs - it saves everyones time to remind patients when scheduling. Also ask patients to bring all current medications in original bottles.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Dr. Johnson - Endocrinology"

echo ""
echo "🔄 CONTINUITY OF CARE"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Oncology",
    "provider_name": "",
    "knowledge_type": "continuity_care",
    "is_continuity_care": true,
    "knowledge_description": "Oncology patients should ALWAYS be scheduled with their original oncologist unless that doctor specifically transfers care. Dont just grab any open slot with available oncologist - cancer patients need consistency and their doctor knows their full history. Check patient history before scheduling.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Oncology - Same Doctor Required"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Utah Valley Hospital – Provo, UT",
    "specialty_service": "General Surgery",
    "provider_name": "",
    "knowledge_type": "continuity_care",
    "is_continuity_care": true,
    "knowledge_description": "Post-surgical follow-ups MUST be with the surgeon who performed the procedure. System should block scheduling with different surgeon in same specialty. Only exception is if the original surgeon is on extended leave - then schedule with covering surgeon and note the reason.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Surgery - Post-Op Same Surgeon"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "McKay-Dee Hospital – Ogden, UT",
    "specialty_service": "Behavioral Health",
    "provider_name": "",
    "knowledge_type": "continuity_care",
    "is_continuity_care": true,
    "knowledge_description": "Mental health patients benefit greatly from seeing the same therapist. Always check patient history and offer their previous providers available slots first. However, patient CAN choose a different provider if they prefer - dont force continuity, just prioritize it.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Behavioral Health - Prefer Same Therapist"

echo ""
echo "🧪 PRE-VISIT REQUIREMENT"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Cardiology",
    "provider_name": "Dr. Sarah Mitchell",
    "knowledge_type": "pre_visit_requirement",
    "is_continuity_care": false,
    "knowledge_description": "Heart failure follow-up appointments require: (1) BNP labs drawn within 48 hours before appointment, (2) Current weight recorded, (3) BP log from home monitoring if patient has blood pressure cuff. If morning appointment and labs needed, patient should be NPO after midnight. Dr. Mitchell will not see patient without recent BNP levels.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Cardiology - BNP Labs Required"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Primary Childrens Hospital – Salt Lake City, UT",
    "specialty_service": "Dermatology",
    "provider_name": "",
    "knowledge_type": "pre_visit_requirement",
    "is_continuity_care": false,
    "knowledge_description": "New dermatology patients coming for mole check should: (1) Take photos of concerning spots before visit, (2) Bring list of ALL current medications including supplements, (3) Wear clothing that allows easy access to areas of concern. Parents of pediatric patients should document when moles first appeared.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Dermatology - Mole Photos + Med List"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "LDS Hospital – Salt Lake City, UT",
    "specialty_service": "Rheumatology",
    "provider_name": "Dr. Anderson",
    "knowledge_type": "pre_visit_requirement",
    "is_continuity_care": false,
    "knowledge_description": "New rheumatology patients MUST have these labs drawn at least 3 days before appointment: CBC, CMP, ESR, CRP, RF (Rheumatoid Factor), and anti-CCP. Dr. Anderson will NOT see new patients without these labs - appointment will be rescheduled. Established patients dont need pre-visit labs unless specifically ordered.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Rheumatology - Required Labs"

echo ""
echo "📋 SCHEDULING WORKFLOW"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Utah Valley Hospital – Provo, UT",
    "specialty_service": "Bariatric Surgery",
    "provider_name": "",
    "knowledge_type": "scheduling_workflow",
    "is_continuity_care": false,
    "knowledge_description": "Bariatric surgery consult workflow: (1) First verify insurance pre-authorization is approved, (2) Schedule nutrition consult FIRST - this is mandatory, (3) Then schedule surgeon consult 2-4 weeks after nutrition appointment, (4) Psychology evaluation can happen concurrently with surgeon consult. Dont schedule surgeon before nutrition - its a waste of everyones time and surgeon wont proceed without nutrition clearance.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Bariatric - Multi-Step Workflow"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "McKay-Dee Hospital – Ogden, UT",
    "specialty_service": "Orthopedic Surgery",
    "provider_name": "",
    "knowledge_type": "scheduling_workflow",
    "is_continuity_care": false,
    "knowledge_description": "Orthopedic post-op follow-up workflow: Check if physical therapy (PT) was ordered. If yes, try to coordinate PT and surgeon follow-up appointments on the same day when possible - patients love one-stop visits and surgeon wants PT progress feedback during the visit. Schedule PT about 30 minutes before surgeon so therapist can give update.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Orthopedic - Coordinate with PT"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Dixie Regional Medical Center – St.George, UT",
    "specialty_service": "Sleep Medicine",
    "provider_name": "",
    "knowledge_type": "scheduling_workflow",
    "is_continuity_care": false,
    "knowledge_description": "Sleep study scheduling workflow: (1) Verify sleep medicine referral is in system, (2) Submit insurance authorization request (takes 3-5 business days), (3) Once approved, call patient to explain home study vs lab study options, (4) Schedule the sleep study, (5) Automatically schedule follow-up appointment 2 weeks after study date for results review with sleep doctor.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Sleep Medicine - Authorization Process"

echo ""
echo "💡 GENERAL KNOWLEDGE"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Intermountain Medical Center – Murray, UT",
    "specialty_service": "Multiple Specialties",
    "provider_name": "",
    "knowledge_type": "general_knowledge",
    "is_continuity_care": false,
    "knowledge_description": "Friday afternoon scheduling: Last appointment slots should be 3 PM because the lab closes at 4 PM and many patients need bloodwork drawn after their visit. Dont schedule 4 PM or later slots on Fridays even if the system allows it - patients get frustrated when they cant get labs done.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Friday Lab Hours"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Primary Childrens Hospital – Salt Lake City, UT",
    "specialty_service": "All Departments",
    "provider_name": "",
    "knowledge_type": "general_knowledge",
    "is_continuity_care": false,
    "knowledge_description": "Interpreter services scheduling: Need 48-hour advance notice for ASL (sign language) interpreters, 24-hour notice for Spanish interpreters. Video remote interpreting is available same-day for other languages. Always note language needs in appointment comments when scheduling so interpreter is ready when patient arrives.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Interpreter Services"

COUNT=$((COUNT + 1))
curl -s -X POST http://localhost:8777/api/v1/knowledge-entries/ \
  -H "Content-Type: application/json" \
  -b /tmp/seed_cookies.txt \
  -d '{
    "facility": "Utah Valley Hospital – Provo, UT",
    "specialty_service": "All Departments",
    "provider_name": "",
    "knowledge_type": "general_knowledge",
    "is_continuity_care": false,
    "knowledge_description": "Parking validation: We only validate parking for appointments lasting over 1 hour. Tell patients during scheduling if theyll need to pay for parking so they can bring cash or card. Validation desk is on first floor near main entrance - direct patients there after long appointments.",
    "status": "published"
  }' > /dev/null && echo "  ✅ [$COUNT/18] Parking Validation"

echo ""
echo "======================================================================"
echo "📊 Summary by Knowledge Type"
echo "======================================================================"
echo "  Diagnosis → Specialty...................   3 entries"
echo "  Provider Preference.....................   3 entries"
echo "  Continuity of Care......................   3 entries"
echo "  Pre-Visit Requirement...................   3 entries"
echo "  Scheduling Workflow.....................   3 entries"
echo "  General Knowledge.......................   3 entries"
echo "  ────────────────────────────────────────────────────"
echo "  TOTAL...................................  18 entries"
echo ""
echo "✅ Knowledge base seeded successfully!"
echo ""
echo "You can now:"
echo "  - Login as Creator and test semantic search"
echo "  - Try autocomplete for providers, specialties, facilities"
echo "  - Test checklist generation for different scenarios"
echo "  - Filter by knowledge type in the Browse view"
echo "======================================================================"
