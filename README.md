# VolunteerIQ — FIFA World Cup 2026
**Every volunteer. Every language. Every decision. Instant.**

AI-powered assistant for stadium volunteers at MetLife Stadium.

## Live Demo
[Add Firebase URL here]

## What it does
- Auto-detects fan language — responds in fan's language + English simultaneously
- Crowd reasoning — Gate C 96% full → redirects to Gate D with full explanation
- Accessibility routing — step-free routes in any language
- Shift briefing — AI-generated per gate per match

## Stack
- Groq llama-3.3-70b-versatile (4 AI agents)
- FastAPI + Cloud Run
- Firebase Hosting
- Firestore

## Run locally
```bash
cd backend && pip install -r requirements.txt
export GROQ_API_KEY=your-key
uvicorn main:app --port 8080 --reload
cd ../frontend && python3 -m http.server 3000
```
