"""
data.py — VolunteerIQ Stadium Knowledge Base
MetLife Stadium, FIFA World Cup 2026
Static data module. All constants in UPPER_CASE.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STADIUM_DATA — Complete MetLife Stadium operational data
# Used by all 4 AI agents as their knowledge base
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STADIUM_DATA: dict = {

    "venue": {
        "name": "MetLife Stadium",
        "city": "East Rutherford, New Jersey, USA",
        "capacity": 82500,
        "volunteer_stations": [
            "Gate A North Entry",
            "Gate B East Entry",
            "Gate C South Entry",
            "Gate D West Entry",
            "Section 100 Concourse",
            "Section 200 Concourse",
            "Section 300 Concourse",
            "Accessibility Services Desk",
            "Lost & Found — Gate B",
            "Medical Station — Section 112",
            "Family Zone — Section 140"
        ]
    },

    "gates": [
        {
            "id": "gate_a",
            "name": "Gate A — North",
            "current_occupancy": 3200,
            "capacity": 4000,
            "density_percent": 80,
            "status": "high",
            "wait_minutes": 12,
            "accessible": True,
            "elevator": True,
            "directions_from_metro": "Turn left from Meadowlands Station, 400m walk",
            "serves_sections": ["101-115", "200-210"],
            "bag_check_lanes": 8,
            "bag_check_wait_minutes": 6
        },
        {
            "id": "gate_b",
            "name": "Gate B — East",
            "current_occupancy": 1200,
            "capacity": 4000,
            "density_percent": 30,
            "status": "available",
            "wait_minutes": 3,
            "accessible": True,
            "elevator": True,
            "directions_from_metro": "Straight ahead from Meadowlands Station, 200m",
            "serves_sections": ["116-130", "211-225"],
            "bag_check_lanes": 8,
            "bag_check_wait_minutes": 2
        },
        {
            "id": "gate_c",
            "name": "Gate C — South",
            "current_occupancy": 3850,
            "capacity": 4000,
            "density_percent": 96,
            "status": "critical",
            "wait_minutes": 22,
            "accessible": False,
            "elevator": False,
            "directions_from_metro": "Turn right from Meadowlands Station, 600m walk",
            "serves_sections": ["131-145", "226-240"],
            "bag_check_lanes": 6,
            "bag_check_wait_minutes": 18
        },
        {
            "id": "gate_d",
            "name": "Gate D — West",
            "current_occupancy": 800,
            "capacity": 4000,
            "density_percent": 20,
            "status": "available",
            "wait_minutes": 2,
            "accessible": True,
            "elevator": True,
            "directions_from_metro": "Bus Route 355 to Gate D stop",
            "serves_sections": ["146-160", "241-255"],
            "bag_check_lanes": 8,
            "bag_check_wait_minutes": 1
        }
    ],

    "accessible_routes": {
        "wheelchair": {
            "gates": ["Gate A", "Gate B", "Gate D"],
            "note": "Gate C has NO wheelchair access — stairs only",
            "elevator_locations": [
                "Gate A lobby — 2 elevators, max 10 persons",
                "Gate B lobby — 2 elevators",
                "Gate D lobby — 3 elevators, largest capacity"
            ],
            "accessible_seating": [
                "Sections 101, 102 — pitch level, front row",
                "Sections 201, 202 — club level with companion seats",
                "Sections 301, 302 — upper bowl, dedicated spaces"
            ],
            "companion_restrooms": [
                "Section 102 concourse",
                "Section 202 concourse",
                "Gate D lobby"
            ]
        },
        "deaf_hoh": {
            "caption_screens": [
                "All concourse screens — real-time captions enabled",
                "Section 115, 130, 145, 160 — dedicated caption screens"
            ],
            "sign_language_interpreters": [
                "Gate B information desk — available 2hrs before kickoff",
                "Accessibility Services Desk — all match hours"
            ],
            "vibrating_wristbands": "Available at Accessibility Services Desk — free"
        },
        "visual_impairment": {
            "audio_description": "Available via app on 97.5FM stadium frequency",
            "guide_dog_relief": "Section 105 outer concourse, designated area",
            "tactile_maps": "Available at Gate A and B information desks"
        }
    },

    "facilities": {
        "restrooms": [
            {"location": "Gate A lobby", "accessible": True, "family": True},
            {"location": "Section 110 concourse", "accessible": True, "family": False},
            {"location": "Section 130 concourse", "accessible": True, "family": True},
            {"location": "Section 200 concourse", "accessible": True, "family": True},
            {"location": "Section 300 concourse", "accessible": False, "family": False}
        ],
        "food": [
            {
                "name": "International Food Hall",
                "location": "Section 220 concourse",
                "options": ["vegetarian", "vegan", "gluten-free", "halal"],
                "languages_spoken": ["English", "Spanish", "Portuguese"],
                "wait_minutes": 8
            },
            {
                "name": "American Grill",
                "location": "Section 110 concourse",
                "options": ["vegetarian"],
                "languages_spoken": ["English"],
                "wait_minutes": 5
            },
            {
                "name": "Grab & Go Kiosks",
                "location": "Sections 105, 115, 125, 205, 215, 305",
                "options": ["vegetarian", "gluten-free"],
                "languages_spoken": ["English", "Spanish"],
                "wait_minutes": 2
            },
            {
                "name": "Halal Kitchen",
                "location": "Section 205 concourse",
                "options": ["halal", "vegetarian", "vegan"],
                "languages_spoken": ["English", "Arabic", "French"],
                "wait_minutes": 10
            },
            {
                "name": "Vegan Paradise",
                "location": "Section 135 concourse",
                "options": ["vegan", "gluten-free", "vegetarian"],
                "languages_spoken": ["English", "Spanish"],
                "wait_minutes": 4
            }
        ],
        "medical": [
            "Section 112 — primary medical station, 24/7",
            "Section 234 — secondary station",
            "Section 312 — upper bowl station",
            "Gate D — field level medical"
        ],
        "prayer_rooms": [
            "Gate B Level 2 — multi-faith room, capacity 20",
            "Gate D Level 3 — multi-faith room, capacity 15"
        ],
        "lost_found": "Gate B information desk",
        "family_zone": "Sections 140-145 — stroller parking, nursing room, play area"
    },

    "transport": {
        "metro": {
            "station": "Meadowlands Station — NJ Transit",
            "walking_time_gate_a": "8 minutes",
            "walking_time_gate_b": "4 minutes",
            "walking_time_gate_c": "12 minutes",
            "walking_time_gate_d": "15 minutes via shuttle",
            "frequency": "Every 10 minutes on match days",
            "last_train": "2 hours after final whistle"
        },
        "bus": {
            "routes": ["355 to Gate A", "356 to Gate B", "357 to Gate D"],
            "frequency": "Every 15 minutes",
            "accessible_buses": "All routes have low-floor accessible buses"
        },
        "rideshare": {
            "zone": "Lot H, Gate D side",
            "walking_time": "5 minutes from Gate D",
            "tip": "Pre-book before leaving seat to avoid surge pricing"
        },
        "parking": {
            "P1": {"gate": "Gate A", "available": 450, "ev": True,
                   "accessible_spaces": 50},
            "P2": {"gate": "Gate C", "available": 1200, "ev": False,
                   "accessible_spaces": 80},
            "P3": {"gate": "Gate D", "available": 800, "ev": True,
                   "accessible_spaces": 40}
        }
    },

    "matches": [
        {
            "match_id": "WC01",
            "teams": "Brazil vs Argentina",
            "kickoff": "19:00 ET",
            "date": "2026-06-15",
            "primary_languages": ["Portuguese", "Spanish"],
            "expected_fans": 81000,
            "sold_out": True
        },
        {
            "match_id": "WC02",
            "teams": "USA vs Mexico",
            "kickoff": "20:00 ET",
            "date": "2026-06-20",
            "primary_languages": ["English", "Spanish"],
            "expected_fans": 82500,
            "sold_out": True
        },
        {
            "match_id": "WC03",
            "teams": "Morocco vs France",
            "kickoff": "15:00 ET",
            "date": "2026-06-25",
            "primary_languages": ["Arabic", "French"],
            "expected_fans": 79000,
            "sold_out": True
        }
    ],

    "volunteer_quick_answers": {
        "lost_child": "Take child to Family Zone Section 140. Call PA desk ext 2100. Log description in VolunteerIQ.",
        "medical": "Call medical team ext 2112. Do not move injured person. Clear 10ft radius. Stay with them.",
        "security_threat": "Call security command ext 911. Do not engage. Move fans away quietly. Wait for response.",
        "fire_alarm": "Follow color-coded exits. Do not use elevators. Nearest exit priority. Do not run.",
        "lost_item": "Direct to Gate B Lost & Found desk. Open until 2hrs after match.",
        "ticket_issue": "Direct to Ticket Resolution Center, Gate A lobby, Level 1."
    },

    "languages": [
        {"code": "en", "name": "English", "flag": "🇺🇸"},
        {"code": "es", "name": "Spanish", "flag": "🇪🇸"},
        {"code": "pt", "name": "Portuguese", "flag": "🇧🇷"},
        {"code": "fr", "name": "French", "flag": "🇫🇷"},
        {"code": "ar", "name": "Arabic", "flag": "🇲🇦"},
        {"code": "hi", "name": "Hindi", "flag": "🇮🇳"},
        {"code": "de", "name": "German", "flag": "🇩🇪"},
        {"code": "ja", "name": "Japanese", "flag": "🇯🇵"}
    ]
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LANGUAGE_FLAGS — Quick lookup for detected language codes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE_FLAGS: dict = {
    "en": "🇺🇸", "es": "🇪🇸", "pt": "🇧🇷",
    "fr": "🇫🇷", "ar": "🇲🇦", "hi": "🇮🇳",
    "de": "🇩🇪", "ja": "🇯🇵", "zh": "🇨🇳",
    "ko": "🇰🇷", "it": "🇮🇹", "nl": "🇳🇱"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DENSITY_THRESHOLDS — Gate crowd level thresholds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DENSITY_THRESHOLDS: dict = {
    "available": 60,   # < 60% = green, open
    "moderate": 79,    # 60-79% = yellow, manageable
    "high": 89,        # 80-89% = orange, monitor closely
    "critical": 100    # 90%+  = red, redirect immediately
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMERGENCY_EXTENSIONS — Critical contact numbers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMERGENCY_EXTENSIONS: dict = {
    "medical": "2112",
    "security": "911",
    "supervisor": "2000",
    "lost_child": "2100",
    "pa_desk": "2100",
    "ticket_resolution": "2050"
}
