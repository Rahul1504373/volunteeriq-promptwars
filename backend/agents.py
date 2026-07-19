"""
agents.py — VolunteerIQ AI Agent Classes
PromptWars Challenge 4: Smart Stadiums & Tournament Ops

4 AI agents powering VolunteerIQ (using Groq llama-3.3-70b-versatile):
1. TranslatorAssistantAgent  — bilingual fan/volunteer response
2. CrowdReasoningAgent       — crowd safety decisions with full reasoning
3. AccessibilityRouterAgent  — step-free routing for fans with special needs
4. SituationBriefingAgent    — real-time shift briefings for volunteers
"""

import json
import logging
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq

# Load .env from same directory as this file
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from data import STADIUM_DATA

logger = logging.getLogger("volunteeriq.agents")

GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_groq_client() -> Groq:
    """Return a configured Groq client using GROQ_API_KEY from env."""
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """
    Make a single Groq API call and return the response text.

    Args:
        system_prompt: The agent's system instruction.
        user_prompt:   The user/context message.

    Returns:
        Response text string from Groq.
    """
    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=800,
        timeout=30,
    )
    return response.choices[0].message.content


def _extract_json(text: str) -> dict:
    """
    Extract and parse the first JSON object found in a text string.
    Strips markdown code fences if present.

    Args:
        text: Raw text potentially containing a JSON object.

    Returns:
        Parsed dict on success, empty dict on failure.
    """
    text = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as exc:
            logger.warning("JSON decode failed: %s", exc)
    return {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLASS 1 — TranslatorAssistantAgent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TranslatorAssistantAgent:
    """
    The core volunteer superpower.
    Fan speaks ANY language → volunteer gets answer in BOTH languages.
    """

    SYSTEM_PROMPT: str = """You are VolunteerIQ, an AI assistant
for FIFA World Cup 2026 stadium volunteers at MetLife Stadium.
A fan has approached a volunteer and asked a question.
The volunteer may not speak the fan's language.

Your job:
1. Detect the language of the fan's question automatically
2. Find the answer from the stadium knowledge provided
3. Give the volunteer TWO outputs simultaneously:
   a) The answer in the FAN'S LANGUAGE (for the fan to read/hear)
   b) The answer in English (for the volunteer to understand)
4. Add a 3-word action hint for the volunteer in [BRACKETS]

Rules:
- Never ask what language — detect automatically
- Be specific: gate names, section numbers, walking times
- For navigation: ALWAYS include reasoning
  ("Gate C is 96% full — go to Gate B instead, 3 min wait")
- For accessibility: always mention step-free alternatives
- For emergencies: fan language first, then call extension
- Keep fan-facing answer under 3 sentences
- Keep volunteer hint under 5 words in [BRACKETS]
- Tone: calm, helpful, confident

Output valid JSON only:
{
  "language_detected": "<full language name e.g. Portuguese>",
  "language_code": "<ISO 639-1 code e.g. pt>",
  "fan_response": "<answer in fan's language>",
  "volunteer_summary": "<answer in English for volunteer>",
  "volunteer_action_hint": "<3-5 words in [BRACKETS]>",
  "is_emergency": false,
  "requires_supervisor": false,
  "relevant_gate": "<gate name or null>",
  "accessibility_flag": false
}"""

    def __init__(self, model: str = GROQ_MODEL) -> None:
        """Initialize the agent."""
        self._model = model

    def assist(self, fan_query: str, gate_context: dict, match_id: str) -> dict:
        """
        Process a fan's question and return a bilingual response.

        Args:
            fan_query:    Raw text from the fan in any language.
            gate_context: Volunteer's current gate dict.
            match_id:     Match identifier e.g. 'WC01'.

        Returns:
            dict with bilingual response and volunteer guidance.
        """
        match_data = next(
            (m for m in STADIUM_DATA["matches"] if m["match_id"] == match_id),
            STADIUM_DATA["matches"][0],
        )

        user_prompt = f"""=== STADIUM KNOWLEDGE ===
Venue: {STADIUM_DATA['venue']['name']}, {STADIUM_DATA['venue']['city']}
Today's match: {match_data['teams']} — kickoff {match_data['kickoff']}
Primary fan languages today: {', '.join(match_data['primary_languages'])}

=== VOLUNTEER'S CURRENT GATE ===
{json.dumps(gate_context, indent=2)}

=== ALL GATE STATUS (for redirect decisions) ===
{json.dumps(STADIUM_DATA['gates'], indent=2)}

=== FACILITIES ===
Food options: {json.dumps(STADIUM_DATA['facilities']['food'], indent=2)}
Restrooms: {json.dumps(STADIUM_DATA['facilities']['restrooms'], indent=2)}
Medical: {STADIUM_DATA['facilities']['medical']}
Prayer rooms: {STADIUM_DATA['facilities']['prayer_rooms']}
Family zone: {STADIUM_DATA['facilities']['family_zone']}
Lost & Found: {STADIUM_DATA['facilities']['lost_found']}

=== ACCESSIBILITY ===
{json.dumps(STADIUM_DATA['accessible_routes'], indent=2)}

=== TRANSPORT ===
Metro: {json.dumps(STADIUM_DATA['transport']['metro'], indent=2)}
Bus: {json.dumps(STADIUM_DATA['transport']['bus'], indent=2)}
Rideshare: {json.dumps(STADIUM_DATA['transport']['rideshare'], indent=2)}

=== EMERGENCY PROTOCOLS ===
{json.dumps(STADIUM_DATA['volunteer_quick_answers'], indent=2)}

=== FAN'S QUESTION ===
{fan_query}

Respond with valid JSON only. No markdown. No explanation outside JSON."""

        try:
            raw = _call_groq(self.SYSTEM_PROMPT, user_prompt)
            result = _extract_json(raw)
            if result:
                return result
        except Exception as exc:
            logger.error("TranslatorAssistantAgent.assist error: %s", exc)

        return {
            "language_detected": "Unknown",
            "language_code": "en",
            "fan_response": "Please wait one moment — I am getting help for you. / Por favor espere — estoy buscando ayuda.",
            "volunteer_summary": "Unable to process query automatically. Please call supervisor ext 2000 for language assistance.",
            "volunteer_action_hint": "[Call supervisor now]",
            "is_emergency": False,
            "requires_supervisor": True,
            "relevant_gate": None,
            "accessibility_flag": False,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLASS 2 — CrowdReasoningAgent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CrowdReasoningAgent:
    """
    Reasons over crowd data and generates actionable decisions
    with full human-readable explanation and multilingual alerts.
    """

    SYSTEM_PROMPT: str = """You are a crowd safety AI for FIFA
World Cup 2026 at MetLife Stadium. You analyze live gate density data
and reason over it to make specific, actionable decisions.

Critical principle: Don't just detect — REASON and DECIDE.

Output valid JSON only:
{
  "overall_risk": "<Low|Medium|High|Critical>",
  "reasoning": "<detailed multi-sentence explanation of WHY>",
  "decision": "<specific action to take RIGHT NOW>",
  "redirect_from": "<gate name or null>",
  "redirect_to": "<gate name or null>",
  "time_to_critical_minutes": null,
  "alert_message": {
    "en": "<crowd alert in English>",
    "es": "<crowd alert in Spanish>",
    "pt": "<crowd alert in Portuguese>"
  },
  "volunteer_instruction": "<what the on-ground volunteer should do>",
  "estimated_wait_if_redirected_minutes": 5
}"""

    def __init__(self, model: str = GROQ_MODEL) -> None:
        """Initialize the agent."""
        self._model = model

    def analyze_and_decide(self, gates: list, match: dict) -> dict:
        """
        Analyze all gate densities and produce a reasoned redirect decision.

        Args:
            gates: List of gate dicts with current_occupancy and capacity.
            match: Current match dict including primary_languages.

        Returns:
            dict with crowd analysis and multilingual alerts.
        """
        enriched_gates = []
        for gate in gates:
            g = dict(gate)
            if g.get("capacity", 0) > 0:
                g["density_percent"] = round(
                    (g["current_occupancy"] / g["capacity"]) * 100, 1
                )
            enriched_gates.append(g)

        user_prompt = f"""=== LIVE GATE DATA ===
{json.dumps(enriched_gates, indent=2)}

=== TODAY'S MATCH ===
{json.dumps(match, indent=2)}

=== CONTEXT ===
Stadium capacity: {STADIUM_DATA['venue']['capacity']}
Accessible gates (wheelchair): Gate A, Gate B, Gate D
Gate C: NO wheelchair access, stairs only

Analyze the data, reason through it step by step, and output
the JSON decision. No markdown. No text outside the JSON object."""

        try:
            raw = _call_groq(self.SYSTEM_PROMPT, user_prompt)
            result = _extract_json(raw)
            if result:
                return result
        except Exception as exc:
            logger.error("CrowdReasoningAgent.analyze_and_decide error: %s", exc)

        return {
            "overall_risk": "Unknown",
            "reasoning": "Unable to complete crowd analysis. Monitor gates manually.",
            "decision": "Contact supervisor ext 2000 if any gate exceeds 90%.",
            "redirect_from": None,
            "redirect_to": None,
            "time_to_critical_minutes": None,
            "alert_message": {
                "en": "Please use all available gates for entry.",
                "es": "Por favor use todas las puertas disponibles para entrar.",
                "pt": "Por favor use todos os portões disponíveis para entrar.",
            },
            "volunteer_instruction": "Manually check each gate and report to supervisor.",
            "estimated_wait_if_redirected_minutes": 5,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLASS 3 — AccessibilityRouterAgent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AccessibilityRouterAgent:
    """
    Handles wheelchair routing, deaf/HoH assistance, visual impairment,
    family routes, and medical needs — in the fan's own language.
    """

    SYSTEM_PROMPT: str = """You are an accessibility specialist AI
for FIFA World Cup 2026 at MetLife Stadium. A volunteer needs to help
a fan with accessibility needs. The fan may not speak English.

Your job:
1. Detect the fan's language automatically
2. Identify the specific accessibility need
3. Provide step-by-step route in FAN'S language
4. Provide same instructions in English for volunteer
5. CRITICAL: Gate C has NO elevator — NEVER route wheelchair users there

Output valid JSON only:
{
  "language_detected": "<full language name>",
  "accessibility_type": "<Wheelchair|Deaf/HoH|Visual Impairment|Family|Medical|Nursing>",
  "fan_instructions": "<step-by-step in fan's language, numbered>",
  "volunteer_escort_needed": false,
  "route_description": "<English route for volunteer>",
  "nearest_facility": "<specific location>",
  "walking_time_minutes": 5,
  "elevator_required": false,
  "elevator_location": null,
  "additional_support": null,
  "emergency_flag": false
}"""

    def __init__(self, model: str = GROQ_MODEL) -> None:
        """Initialize the agent."""
        self._model = model

    def route(self, fan_query: str, current_location: str) -> dict:
        """
        Generate an accessible route for a fan with special needs.

        Args:
            fan_query:        Raw text from the fan in any language.
            current_location: Volunteer's current gate/section.

        Returns:
            dict with accessible routing in fan's language and English.
        """
        user_prompt = f"""=== FULL ACCESSIBILITY DATA ===
{json.dumps(STADIUM_DATA['accessible_routes'], indent=2)}

=== ALL GATES (accessible status) ===
{json.dumps([
    {k: v for k, v in g.items()
     if k in ('id', 'name', 'accessible', 'elevator', 'density_percent', 'status', 'wait_minutes')}
    for g in STADIUM_DATA['gates']
], indent=2)}

=== FACILITIES ===
Medical stations: {STADIUM_DATA['facilities']['medical']}
Family zone: {STADIUM_DATA['facilities']['family_zone']}
Restrooms (accessible): {json.dumps([r for r in STADIUM_DATA['facilities']['restrooms'] if r['accessible']], indent=2)}

=== VOLUNTEER'S CURRENT LOCATION ===
{current_location}

=== FAN'S QUERY ===
{fan_query}

Output valid JSON only. No markdown. No text outside the JSON object."""

        try:
            raw = _call_groq(self.SYSTEM_PROMPT, user_prompt)
            result = _extract_json(raw)
            if result:
                return result
        except Exception as exc:
            logger.error("AccessibilityRouterAgent.route error: %s", exc)

        return {
            "language_detected": "Unknown",
            "accessibility_type": "General Assistance",
            "fan_instructions": "Please follow the volunteer to the Accessibility Services Desk for full assistance.",
            "volunteer_escort_needed": True,
            "route_description": "Escort fan to Accessibility Services Desk near Gate B.",
            "nearest_facility": "Accessibility Services Desk — near Gate B",
            "walking_time_minutes": 5,
            "elevator_required": False,
            "elevator_location": None,
            "additional_support": "Accessibility Services Desk staff available all match hours.",
            "emergency_flag": False,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLASS 4 — SituationBriefingAgent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SituationBriefingAgent:
    """
    Gives volunteers a real-time AI-generated briefing every 15 minutes.
    Tells them what's happening, what to expect, and when to escalate.
    """

    SYSTEM_PROMPT: str = """You are a shift briefing AI for
FIFA World Cup 2026 stadium volunteers at MetLife Stadium.
Generate a 60-second briefing a volunteer can read quickly.

Be specific, practical, and actionable.
Address the volunteer directly (use 'You' / 'Your gate').

Format your response EXACTLY using these section headers:

GATE STATUS: <one clear sentence about their gate right now>

CROWD FORECAST: <next 30 minutes prediction>

LANGUAGES TODAY: <which languages to expect and key phrases>

TOP 3 QUESTIONS YOU WILL GET:
1. <most common question>
2. <second most common>
3. <third most common>

WATCH OUT FOR: <1-2 specific risks this shift>

ESCALATE IF: <clear conditions requiring supervisor>"""

    def __init__(self, model: str = GROQ_MODEL) -> None:
        """Initialize the agent."""
        self._model = model

    def brief(self, volunteer_gate: str, match: dict, gates: list) -> dict:
        """
        Generate a structured real-time shift briefing.

        Args:
            volunteer_gate: Gate ID e.g. 'gate_c'.
            match:          Today's match dict.
            gates:          All gate status data.

        Returns:
            dict with parsed briefing sections.
        """
        gate_data = next(
            (g for g in gates if g["id"] == volunteer_gate),
            gates[0],
        )

        user_prompt = f"""=== YOUR GATE ===
{json.dumps(gate_data, indent=2)}

=== TODAY'S MATCH ===
{json.dumps(match, indent=2)}

=== ALL GATES STATUS ===
{json.dumps(gates, indent=2)}

=== STADIUM CONTEXT ===
Emergency numbers: Medical ext 2112, Security ext 911, Supervisor ext 2000
Accessibility desk: near Gate B
Family zone: Sections 140-145

Generate the briefing now. Use the exact header format specified."""

        raw_text = ""
        try:
            raw_text = _call_groq(self.SYSTEM_PROMPT, user_prompt).strip()
        except Exception as exc:
            logger.error("SituationBriefingAgent.brief error: %s", exc)
            raw_text = (
                f"GATE STATUS: {gate_data['name']} is at {gate_data['density_percent']}% capacity.\n"
                f"CROWD FORECAST: Monitor current flow and redirect if density exceeds 90%.\n"
                f"LANGUAGES TODAY: Expect {', '.join(match['primary_languages'])} speakers.\n"
                "TOP 3 QUESTIONS YOU WILL GET:\n1. Where are the restrooms?\n2. Where is my seat?\n3. Where is food?\n"
                "WATCH OUT FOR: Gate congestion during peak entry.\n"
                "ESCALATE IF: Gate density exceeds 90% or any medical emergency."
            )

        sections = _parse_briefing_sections(raw_text)
        sections["raw_text"] = raw_text
        return sections


def _parse_briefing_sections(text: str) -> dict:
    """
    Parse a SituationBriefingAgent response into a structured dict.

    Args:
        text: Raw text response with section headers.

    Returns:
        dict with keys: gate_status, crowd_forecast, languages_today,
        top_3_questions, watch_out_for, escalate_if.
    """
    header_map: dict[str, str] = {
        "## GATE STATUS:": "gate_status", "GATE STATUS:": "gate_status",
        "## CROWD FORECAST:": "crowd_forecast", "CROWD FORECAST:": "crowd_forecast",
        "## LANGUAGES TODAY:": "languages_today", "LANGUAGES TODAY:": "languages_today",
        "## TOP 3 QUESTIONS YOU WILL GET:": "top_3_questions", "TOP 3 QUESTIONS YOU WILL GET:": "top_3_questions",
        "## WATCH OUT FOR:": "watch_out_for", "WATCH OUT FOR:": "watch_out_for",
        "## ESCALATE IF:": "escalate_if", "ESCALATE IF:": "escalate_if",
    }

    result: dict[str, str] = {v: "" for v in header_map.values()}
    current_key: str | None = None

    for line in text.splitlines():
        matched = False
        for header, key in header_map.items():
            if line.strip().upper().startswith(header.upper()):
                current_key = key
                remainder = line.strip()[len(header):].strip()
                if remainder:
                    result[current_key] = remainder
                matched = True
                break
        if not matched and current_key:
            separator = "\n" if result[current_key] else ""
            result[current_key] += separator + line.rstrip()

    for key in result:
        result[key] = result[key].strip()
        if not result[key]:
            result[key] = "Information not available — contact supervisor."

    return result
