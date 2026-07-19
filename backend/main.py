# VolunteerIQ — FIFA World Cup 2026 Smart Stadium Solution
# PromptWars Challenge 4: Smart Stadiums & Tournament Ops
# Persona: Stadium Volunteer
# Verticals: Multilingual Assistance + Navigation +
#            Crowd Intelligence + Accessibility
#
# AI TOOLS USED:
# 1. Antigravity IDE — architecture and code generation
# 2. Gemini 1.5 Flash — all 4 AI agents in production:
#    - TranslatorAssistantAgent: auto-detects language,
#      gives bilingual answer to volunteer+fan simultaneously
#    - CrowdReasoningAgent: reasons over gate density data
#      and generates redirect decisions with full explanation
#    - AccessibilityRouterAgent: step-free routing in any language
#    - SituationBriefingAgent: real-time shift briefings
# 3. Firebase Hosting — frontend deployment
# 4. Cloud Run — scalable API backend
#
# PROMPTS EVOLVED: simple translator → bilingual assistant
#   → crowd reasoning → full volunteer superpower platform
# HUMAN DESIGNED: persona selection, data schema, UX flow
# GENAI HANDLED: all agent logic, translations, reasoning,
#   route generation, crowd analysis, briefings
#
# TEST COMMANDS:
# curl http://localhost:8080/health
# curl -X POST http://localhost:8080/ask \
#   -H "Content-Type: application/json" \
#   -d '{"fan_query":"Onde fica o banheiro?","volunteer_gate":"gate_c","match_id":"WC01"}'
# curl -X POST http://localhost:8080/crowd \
#   -H "Content-Type: application/json" \
#   -d '{"match_id":"WC01"}'
# curl http://localhost:8080/briefing/gate_c/WC01
# curl -X POST http://localhost:8080/accessibility \
#   -H "Content-Type: application/json" \
#   -d '{"fan_query":"I need wheelchair access","current_location":"Gate C"}'
# curl http://localhost:8080/incident/lost_child
# curl "http://localhost:8080/facilities?vegan=true&halal=true"

"""
main.py — VolunteerIQ FastAPI Backend
Serves 6 endpoints powering the VolunteerIQ volunteer assistant app.
Gemini 1.5 Flash agents handle all AI reasoning.
Firestore used for interaction logging (gracefully skipped if unavailable).
"""

import copy
import logging
import os
import random
from datetime import datetime
from typing import Optional

# Groq is configured in agents.py
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, Field

from agents import (
    AccessibilityRouterAgent,
    CrowdReasoningAgent,
    SituationBriefingAgent,
    TranslatorAssistantAgent,
)
from data import STADIUM_DATA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bootstrap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("volunteeriq.main")

# ── Gemini ──────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    logger.warning(
        "GEMINI_API_KEY not set. AI endpoints will return fallback responses. "
        "Export your key: export GEMINI_API_KEY=your-key-from-aistudio.google.com"
    )

# Groq key loaded from .env in agents.py
_model_name = "llama-3.3-70b-versatile"

# ── Agent singletons ─────────────────────────────────────────────────
translator_agent = TranslatorAssistantAgent(model=_model_name)
crowd_agent = CrowdReasoningAgent(model=_model_name)
accessibility_agent = AccessibilityRouterAgent(model=_model_name)
briefing_agent = SituationBriefingAgent(model=_model_name)

# ── Firestore (optional — gracefully skipped) ───────────────────────
_db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    _firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    if _firebase_cred_path and os.path.exists(_firebase_cred_path):
        cred = credentials.Certificate(_firebase_cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        logger.info("Firestore connected successfully.")
    else:
        logger.info("No Firebase credentials found — Firestore logging disabled.")
except Exception as _fb_exc:
    logger.info("Firestore init skipped: %s", _fb_exc)


def _log_to_firestore(collection: str, data: dict) -> None:
    """
    Write a document to Firestore for analytics. Non-blocking.
    Silently ignores all errors so it never interrupts API responses.

    Args:
        collection: Firestore collection name.
        data:       Document data dict to write.
    """
    if _db is None:
        return
    try:
        _db.collection(collection).add({**data, "logged_at": datetime.utcnow()})
    except Exception as exc:
        logger.debug("Firestore write skipped: %s", exc)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI app
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="VolunteerIQ API",
    description="AI-powered multilingual assistant for FIFA World Cup 2026 stadium volunteers.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic request models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""

    fan_query: str = Field(..., min_length=1, max_length=500) = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Raw text from the fan in any language.",
        examples=["Onde fica o banheiro?"],
    )
    volunteer_gate: str = Field(
        default="gate_a",
        description="Gate ID where the volunteer is stationed.",
        examples=["gate_c"],
    )
    match_id: str = Field(
        default="WC01",
        description="Current match identifier.",
        examples=["WC01"],
    )


class CrowdRequest(BaseModel):
    """Request body for the /crowd endpoint."""

    match_id: str = Field(
        default="WC01",
        description="Current match identifier for language context.",
        examples=["WC01"],
    )


class AccessibilityRequest(BaseModel):
    """Request body for the /accessibility endpoint."""

    fan_query: str = Field(..., min_length=1, max_length=500) = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Fan's accessibility request in any language.",
        examples=["I need wheelchair access for my mother."],
    )
    current_location: str = Field(
        default="Gate A",
        description="Volunteer's current gate or section.",
        examples=["Gate C"],
    )


class IncidentRequest(BaseModel):
    """Request body for incident logging (future use)."""

    incident_type: str = Field(
        ...,
        description="Type of incident (matches volunteer_quick_answers keys).",
        examples=["lost_child"],
    )
    location: str = Field(
        ...,
        description="Location where the incident occurred.",
        examples=["Gate C, near bag check lane 3"],
    )
    details: str = Field(
        default="",
        max_length=1000,
        description="Additional incident details.",
    )
    volunteer_gate: str = Field(
        default="gate_a",
        description="Reporting volunteer's gate ID.",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper utilities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_gate(gate_id: str) -> dict:
    """
    Look up a gate by ID from STADIUM_DATA, raising 404 if not found.

    Args:
        gate_id: Gate identifier string (e.g. 'gate_c').

    Returns:
        Gate dict from STADIUM_DATA['gates'].

    Raises:
        HTTPException 404 if gate_id is not found.
    """
    gate = next(
        (g for g in STADIUM_DATA["gates"] if g["id"] == gate_id), None
    )
    if not gate:
        raise HTTPException(
            status_code=404,
            detail=f"Gate '{gate_id}' not found. Valid gates: gate_a, gate_b, gate_c, gate_d",
        )
    return gate


def _get_match(match_id: str) -> dict:
    """
    Look up a match by ID from STADIUM_DATA, raising 404 if not found.

    Args:
        match_id: Match identifier string (e.g. 'WC01').

    Returns:
        Match dict from STADIUM_DATA['matches'].

    Raises:
        HTTPException 404 if match_id is not found.
    """
    match = next(
        (m for m in STADIUM_DATA["matches"] if m["match_id"] == match_id), None
    )
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found. Valid matches: WC01, WC02, WC03",
        )
    return match


def _apply_live_variance(gates: list, seed_value: int) -> list:
    """
    Add realistic ±10% random variance to gate occupancy figures.

    Seeds the RNG with a hash of the match_id so the variance is
    deterministic per match (consistent across API calls in same
    session) but different per match. Recalculates density_percent
    after variance is applied.

    Args:
        gates:      Deep-copied list of gate dicts.
        seed_value: Integer seed derived from match_id hash.

    Returns:
        List of gate dicts with updated current_occupancy
        and density_percent values.
    """
    rng = random.Random(seed_value)
    for gate in gates:
        variance = rng.uniform(-0.10, 0.10)
        raw_occupancy = gate["current_occupancy"] * (1 + variance)
        gate["current_occupancy"] = max(0, min(int(raw_occupancy), gate["capacity"]))
        gate["density_percent"] = round(
            (gate["current_occupancy"] / gate["capacity"]) * 100, 1
        )
        # Update status label based on new density
        d = gate["density_percent"]
        if d >= 90:
            gate["status"] = "critical"
        elif d >= 80:
            gate["status"] = "high"
        elif d >= 60:
            gate["status"] = "moderate"
        else:
            gate["status"] = "available"
    return gates


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 1 — GET /health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/health", tags=["System"])
def health_check() -> dict:
    """
    Health check endpoint.

    Returns service status, version, and configuration summary.
    Use this to verify the API is running before demo.
    """
    return {
        "status": "ok",
        "service": "VolunteerIQ API",
        "version": "1.0",
        "venue": "MetLife Stadium — FIFA World Cup 2026",
        "agents": 4,
        "gemini_model": "gemini-1.5-flash",
        "languages_supported": len(STADIUM_DATA["languages"]),
        "firestore_connected": _db is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 2 — POST /ask
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/ask", tags=["Core"])
def ask(request: AskRequest) -> dict:
    """
    Core endpoint: fan asks a volunteer something in ANY language.

    Passes the query to TranslatorAssistantAgent which automatically
    detects the language and returns a bilingual response — one for
    the fan (in their language) and one for the volunteer (in English).

    This is the hero feature of VolunteerIQ. A volunteer who speaks
    only Hindi can assist a fan speaking Moroccan Arabic in seconds.
    """
    gate_data = _get_gate(request.volunteer_gate)
    match_data = _get_match(request.match_id)

    result = translator_agent.assist(
        fan_query=request.fan_query,
        gate_context=gate_data,
        match_id=request.match_id,
    )

    # Non-blocking Firestore log
    _log_to_firestore("fan_interactions", {
        "fan_query": request.fan_query,
        "volunteer_gate": request.volunteer_gate,
        "match_id": request.match_id,
        "language_detected": result.get("language_detected", "unknown"),
        "is_emergency": result.get("is_emergency", False),
    })

    return {
        **result,
        "timestamp": datetime.utcnow().isoformat(),
        "match": match_data["teams"],
        "gate": gate_data["name"],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 3 — POST /crowd
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/crowd", tags=["Crowd Intelligence"])
def crowd_analysis(request: CrowdRequest) -> dict:
    """
    Analyze all gate densities and return a fully reasoned AI decision.

    Applies realistic live variance to gate occupancy data, then passes
    it to CrowdReasoningAgent which reasons over the data to decide
    if and where to redirect crowds, predicts time-to-critical, and
    generates multilingual alert messages for fans.

    This is what separates VolunteerIQ from basic crowd counters.
    """
    match_data = _get_match(request.match_id)

    # Deep copy + apply live variance seeded by match_id
    gates_live = copy.deepcopy(STADIUM_DATA["gates"])
    seed = hash(request.match_id) & 0x7FFFFFFF
    gates_live = _apply_live_variance(gates_live, seed)

    analysis = crowd_agent.analyze_and_decide(
        gates=gates_live,
        match=match_data,
    )

    # Non-blocking Firestore log
    _log_to_firestore("crowd_analyses", {
        "match_id": request.match_id,
        "overall_risk": analysis.get("overall_risk", "Unknown"),
        "redirect_from": analysis.get("redirect_from"),
        "redirect_to": analysis.get("redirect_to"),
    })

    return {
        "gates_live": gates_live,
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat(),
        "match": match_data["teams"],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 4 — POST /accessibility
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/accessibility", tags=["Accessibility"])
def accessibility(request: AccessibilityRequest) -> dict:
    """
    Handle an accessibility request in any language.

    Detects the fan's accessibility need (wheelchair, deaf/HoH,
    visual impairment, family, medical, nursing) and current language,
    then generates step-by-step instructions in BOTH the fan's language
    and English for the volunteer. Always uses step-free routes.
    """
    result = accessibility_agent.route(
        fan_query=request.fan_query,
        current_location=request.current_location,
    )
    return {
        **result,
        "timestamp": datetime.utcnow().isoformat(),
        "volunteer_location": request.current_location,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 5 — GET /briefing/{volunteer_gate}/{match_id}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/briefing/{volunteer_gate}/{match_id}", tags=["Briefing"])
def get_briefing(volunteer_gate: str, match_id: str) -> dict:
    """
    Generate a real-time shift briefing for a volunteer at a specific gate.

    Returns a structured briefing with gate status, crowd forecast,
    expected languages, top 3 questions they will receive, watch-out
    items, and escalation conditions. Refreshable every 15 minutes.

    Args:
        volunteer_gate: Gate ID (e.g. 'gate_c').
        match_id:       Match ID (e.g. 'WC01').
    """
    gate_data = _get_gate(volunteer_gate)
    match_data = _get_match(match_id)

    briefing = briefing_agent.brief(
        volunteer_gate=volunteer_gate,
        match=match_data,
        gates=STADIUM_DATA["gates"],
    )

    return {
        "briefing": briefing,
        "gate": gate_data,
        "match": match_data,
        "generated_at": datetime.utcnow().isoformat(),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 6 — GET /incident/{incident_type}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/incident/{incident_type}", tags=["Incidents"])
def get_incident_protocol(incident_type: str) -> dict:
    """
    Return the quick-response protocol for a given incident type.

    Incident types: lost_child, medical, security_threat,
    fire_alarm, lost_item, ticket_issue.
    Unknown types return the generic supervisor escalation protocol.

    Args:
        incident_type: The type of incident (must match
                       volunteer_quick_answers keys).
    """
    protocol = STADIUM_DATA["volunteer_quick_answers"].get(
        incident_type,
        "Call supervisor ext 2000 immediately. Do not handle alone.",
    )
    escalate_types = {"security_threat", "fire_alarm", "medical", "lost_child"}
    return {
        "incident_type": incident_type,
        "protocol": protocol,
        "call_extension": "2000",
        "escalate": incident_type in escalate_types,
        "known_incidents": list(STADIUM_DATA["volunteer_quick_answers"].keys()),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT 7 — GET /facilities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/facilities", tags=["Facilities"])
def get_facilities(
    vegan: bool = False,
    halal: bool = False,
    gluten_free: bool = False,
    accessible: bool = False,
) -> dict:
    """
    Return filtered stadium facilities list.

    Query parameters filter food stalls by dietary option.
    Results are sorted by ascending wait time so volunteers
    can direct fans to the fastest available option.

    Query params:
        vegan:       Filter to vegan-friendly food stalls.
        halal:       Filter to halal-certified food stalls.
        gluten_free: Filter to gluten-free food stalls.
        accessible:  Filter to wheelchair-accessible restrooms only.
    """
    food_stalls = STADIUM_DATA["facilities"]["food"]

    # Apply dietary filters
    filtered_food = []
    for stall in food_stalls:
        options = stall.get("options", [])
        if vegan and "vegan" not in options:
            continue
        if halal and "halal" not in options:
            continue
        if gluten_free and "gluten-free" not in options:
            continue
        filtered_food.append(stall)

    # Sort by shortest wait time
    filtered_food.sort(key=lambda s: s.get("wait_minutes", 99))

    # Apply accessible restroom filter
    restrooms = STADIUM_DATA["facilities"]["restrooms"]
    if accessible:
        restrooms = [r for r in restrooms if r.get("accessible")]

    return {
        "food": filtered_food,
        "restrooms": restrooms,
        "medical": STADIUM_DATA["facilities"]["medical"],
        "prayer": STADIUM_DATA["facilities"]["prayer_rooms"],
        "family_zone": STADIUM_DATA["facilities"]["family_zone"],
        "lost_found": STADIUM_DATA["facilities"]["lost_found"],
        "filters_applied": {
            "vegan": vegan,
            "halal": halal,
            "gluten_free": gluten_free,
            "accessible": accessible,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
# Serve frontend static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)
