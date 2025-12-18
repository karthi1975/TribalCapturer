#!/usr/bin/env python3
"""
Seed Railway database with all 27 knowledge entries.
Run this after Railway deployment to populate sample data.

Usage:
    python seed_railway_data.py https://your-backend.railway.app
"""
import sys
import requests
import time

def seed_railway(base_url: str):
    """Seed all knowledge entries to Railway deployment"""

    print("=" * 80)
    print("🌱 Seeding Railway Database with Knowledge Entries")
    print("=" * 80)
    print(f"Target: {base_url}")
    print()

    # Login as MA
    print("🔐 Logging in as MA...")
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": "ma1@tribaliq.com", "password": "TestPassword123!"}
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return False

    session = requests.Session()
    session.cookies.update(response.cookies)
    print("✅ Login successful")
    print()

    # Sample entries for all 6 knowledge types
    entries = [
        # DIAGNOSIS → SPECIALTY (3 entries)
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Rheumatology",
            "provider_name": "",
            "knowledge_type": "diagnosis_specialty",
            "is_continuity_care": False,
            "knowledge_description": "Patient with new diagnosis of Crohn's disease needs appointment with Rheumatologist. Important: Check if GI consult has been completed first - many rheumatologists want GI evaluation done before starting rheumatology care. If no GI consult, schedule GI first, then rheumatology 2-4 weeks later.",
            "status": "published"
        },
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Cardiology",
            "provider_name": "",
            "knowledge_type": "diagnosis_specialty",
            "is_continuity_care": False,
            "knowledge_description": "New MI (myocardial infarction) patients need Cardiology follow-up within 2 weeks of hospital discharge. Schedule stress test for 4-6 weeks post-MI if ordered by cardiologist. Mark as urgent priority when scheduling.",
            "status": "published"
        },
        {
            "facility": "Utah Valley Hospital – Provo, UT",
            "specialty_service": "Endocrinology",
            "provider_name": "",
            "knowledge_type": "diagnosis_specialty",
            "is_continuity_care": False,
            "knowledge_description": "Hypothyroid patients with TSH levels >10 need Endocrinology referral. If TSH is between 5-10, PCP can manage unless patient has severe symptoms or is pregnant. Always check most recent TSH before scheduling endo.",
            "status": "published"
        },

        # PROVIDER PREFERENCE (3 entries)
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Cardiology",
            "provider_name": "Dr. Sarah Mitchell",
            "knowledge_type": "provider_preference",
            "is_continuity_care": False,
            "knowledge_description": "Dr. Mitchell prefers new patients in afternoon slots (after 1 PM) because she reviews charts in the morning. Complex cardiac cases need 60-minute appointments, not standard 30-minute slots. She also requires recent EKG results uploaded before the appointment.",
            "status": "published"
        },
        {
            "facility": "Primary Childrens Hospital – Salt Lake City, UT",
            "specialty_service": "Pediatric Cardiology",
            "provider_name": "Dr. Martinez",
            "knowledge_type": "provider_preference",
            "is_continuity_care": False,
            "knowledge_description": "Dr. Martinez only sees pediatric cardiology patients on Tuesdays and Thursdays. Don't schedule pediatric patients on other days even if calendar shows availability - those slots are for adult patients. All pediatric echo studies should be scheduled same day as appointment when possible.",
            "status": "published"
        },
        {
            "facility": "LDS Hospital – Salt Lake City, UT",
            "specialty_service": "Endocrinology",
            "provider_name": "Dr. Johnson",
            "knowledge_type": "provider_preference",
            "is_continuity_care": False,
            "knowledge_description": "Dr. Johnson requires all diabetic patients to bring glucose logs from past 2 weeks to appointment. She will reschedule if patient doesn't have logs - it saves everyone's time to remind patients when scheduling. Also ask patients to bring all current medications in original bottles.",
            "status": "published"
        },

        # CONTINUITY OF CARE (3 entries)
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Oncology",
            "provider_name": "",
            "knowledge_type": "continuity_care",
            "is_continuity_care": True,
            "knowledge_description": "Oncology patients should ALWAYS be scheduled with their original oncologist unless that doctor specifically transfers care. Don't just grab any open slot with available oncologist - cancer patients need consistency and their doctor knows their full history. Check patient history before scheduling.",
            "status": "published"
        },
        {
            "facility": "Utah Valley Hospital – Provo, UT",
            "specialty_service": "General Surgery",
            "provider_name": "",
            "knowledge_type": "continuity_care",
            "is_continuity_care": True,
            "knowledge_description": "Post-surgical follow-ups MUST be with the surgeon who performed the procedure. System should block scheduling with different surgeon in same specialty. Only exception is if the original surgeon is on extended leave - then schedule with covering surgeon and note the reason.",
            "status": "published"
        },
        {
            "facility": "McKay-Dee Hospital – Ogden, UT",
            "specialty_service": "Behavioral Health",
            "provider_name": "",
            "knowledge_type": "continuity_care",
            "is_continuity_care": True,
            "knowledge_description": "Mental health patients benefit greatly from seeing the same therapist. Always check patient history and offer their previous provider's available slots first. However, patient CAN choose a different provider if they prefer - don't force continuity, just prioritize it.",
            "status": "published"
        },

        # PRE-VISIT REQUIREMENT (4 entries)
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Cardiology",
            "provider_name": "Dr. Sarah Mitchell",
            "knowledge_type": "pre_visit_requirement",
            "is_continuity_care": False,
            "knowledge_description": "Heart failure follow-up appointments require: (1) BNP labs drawn within 48 hours before appointment, (2) Current weight recorded, (3) BP log from home monitoring if patient has blood pressure cuff. If morning appointment and labs needed, patient should be NPO after midnight. Dr. Mitchell will not see patient without recent BNP levels.",
            "status": "published"
        },
        {
            "facility": "Primary Childrens Hospital – Salt Lake City, UT",
            "specialty_service": "Dermatology",
            "provider_name": "",
            "knowledge_type": "pre_visit_requirement",
            "is_continuity_care": False,
            "knowledge_description": "New dermatology patients coming for mole check should: (1) Take photos of concerning spots before visit, (2) Bring list of ALL current medications including supplements, (3) Wear clothing that allows easy access to areas of concern. Parents of pediatric patients should document when moles first appeared.",
            "status": "published"
        },
        {
            "facility": "LDS Hospital – Salt Lake City, UT",
            "specialty_service": "Rheumatology",
            "provider_name": "Dr. Anderson",
            "knowledge_type": "pre_visit_requirement",
            "is_continuity_care": False,
            "knowledge_description": "New rheumatology patients MUST have these labs drawn at least 3 days before appointment: CBC, CMP, ESR, CRP, RF (Rheumatoid Factor), and anti-CCP. Dr. Anderson will NOT see new patients without these labs - appointment will be rescheduled. Established patients don't need pre-visit labs unless specifically ordered.",
            "status": "published"
        },
        {
            "facility": "Utah Valley Hospital – Provo, UT",
            "specialty_service": "Gastroenterology",
            "provider_name": "Dr. James Anderson",
            "knowledge_type": "pre_visit_requirement",
            "is_continuity_care": True,
            "knowledge_description": "Crohn's disease patients need GI consult completed before scheduling with rheumatology. Always check patient history for previous GI visits and schedule with same gastroenterologist if available.",
            "status": "published"
        },

        # SCHEDULING WORKFLOW (3 entries)
        {
            "facility": "Utah Valley Hospital – Provo, UT",
            "specialty_service": "Bariatric Surgery",
            "provider_name": "",
            "knowledge_type": "scheduling_workflow",
            "is_continuity_care": False,
            "knowledge_description": "Bariatric surgery consult workflow: (1) First verify insurance pre-authorization is approved, (2) Schedule nutrition consult FIRST - this is mandatory, (3) Then schedule surgeon consult 2-4 weeks after nutrition appointment, (4) Psychology evaluation can happen concurrently with surgeon consult. Don't schedule surgeon before nutrition - it's a waste of everyone's time and surgeon won't proceed without nutrition clearance.",
            "status": "published"
        },
        {
            "facility": "McKay-Dee Hospital – Ogden, UT",
            "specialty_service": "Orthopedic Surgery",
            "provider_name": "",
            "knowledge_type": "scheduling_workflow",
            "is_continuity_care": False,
            "knowledge_description": "Orthopedic post-op follow-up workflow: Check if physical therapy (PT) was ordered. If yes, try to coordinate PT and surgeon follow-up appointments on the same day when possible - patients love one-stop visits and surgeon wants PT progress feedback during the visit. Schedule PT about 30 minutes before surgeon so therapist can give update.",
            "status": "published"
        },
        {
            "facility": "Dixie Regional Medical Center – St.George, UT",
            "specialty_service": "Sleep Medicine",
            "provider_name": "",
            "knowledge_type": "scheduling_workflow",
            "is_continuity_care": False,
            "knowledge_description": "Sleep study scheduling workflow: (1) Verify sleep medicine referral is in system, (2) Submit insurance authorization request (takes 3-5 business days), (3) Once approved, call patient to explain home study vs lab study options, (4) Schedule the sleep study, (5) Automatically schedule follow-up appointment 2 weeks after study date for results review with sleep doctor.",
            "status": "published"
        },

        # GENERAL KNOWLEDGE (5 entries)
        {
            "facility": "Intermountain Medical Center – Murray, UT",
            "specialty_service": "Multiple Specialties",
            "provider_name": "",
            "knowledge_type": "general_knowledge",
            "is_continuity_care": False,
            "knowledge_description": "Friday afternoon scheduling: Last appointment slots should be 3 PM because the lab closes at 4 PM and many patients need bloodwork drawn after their visit. Don't schedule 4 PM or later slots on Fridays even if the system allows it - patients get frustrated when they can't get labs done.",
            "status": "published"
        },
        {
            "facility": "Primary Childrens Hospital – Salt Lake City, UT",
            "specialty_service": "All Departments",
            "provider_name": "",
            "knowledge_type": "general_knowledge",
            "is_continuity_care": False,
            "knowledge_description": "Interpreter services scheduling: Need 48-hour advance notice for ASL (sign language) interpreters, 24-hour notice for Spanish interpreters. Video remote interpreting is available same-day for other languages. Always note language needs in appointment comments when scheduling so interpreter is ready when patient arrives.",
            "status": "published"
        },
        {
            "facility": "Utah Valley Hospital – Provo, UT",
            "specialty_service": "All Departments",
            "provider_name": "",
            "knowledge_type": "general_knowledge",
            "is_continuity_care": False,
            "knowledge_description": "Parking validation: We only validate parking for appointments lasting over 1 hour. Tell patients during scheduling if they'll need to pay for parking so they can bring cash or card. Validation desk is on first floor near main entrance - direct patients there after long appointments.",
            "status": "published"
        },
        {
            "facility": "American Fork Hospital – American Fork, UT",
            "specialty_service": "Neurology",
            "provider_name": "",
            "knowledge_type": "diagnosis_specialty",
            "is_continuity_care": False,
            "knowledge_description": "Patients with new seizure diagnosis need Neurology referral within 2 weeks. If first seizure, schedule EEG before neurology appointment. Urgent if patient had status epilepticus - schedule within 48 hours.",
            "status": "published"
        },
        {
            "facility": "Riverton Hospital – Riverton, UT",
            "specialty_service": "Gastroenterology",
            "provider_name": "Dr. Lisa Chen",
            "knowledge_type": "provider_preference",
            "is_continuity_care": False,
            "knowledge_description": "Dr. Chen requires colonoscopy prep instructions to be sent 7 days before procedure. She prefers morning procedures (7-11 AM) for better prep compliance. Always ask patient about ride home - Dr. Chen will not proceed without confirmed transportation.",
            "status": "published"
        },
    ]

    print(f"📝 Creating {len(entries)} knowledge entries...")
    print()

    success_count = 0

    for i, entry in enumerate(entries, 1):
        try:
            response = session.post(
                f"{base_url}/api/v1/knowledge-entries/",
                json=entry
            )

            if response.status_code == 201:
                success_count += 1
                data = response.json()
                print(f"✅ [{i}/{len(entries)}] {entry['knowledge_type']}: {entry['specialty_service']}")
            else:
                print(f"❌ [{i}/{len(entries)}] Failed: {response.status_code} - {response.text[:100]}")

            time.sleep(0.1)  # Small delay to avoid rate limiting

        except Exception as e:
            print(f"❌ [{i}/{len(entries)}] Error: {e}")

    print()
    print("=" * 80)
    print(f"✅ Seeding Complete: {success_count}/{len(entries)} entries created")
    print("=" * 80)

    return success_count == len(entries)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_railway_data.py <railway-backend-url>")
        print("Example: python seed_railway_data.py https://tribalcapturer-backend.railway.app")
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')
    success = seed_railway(base_url)

    sys.exit(0 if success else 1)
