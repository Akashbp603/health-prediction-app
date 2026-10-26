"""AI health-risk remarks via the Anthropic Messages API.

Set ANTHROPIC_API_KEY in your environment (never commit it).
If the key is missing or the call fails, a clearly labelled rule-based
remark is returned so the app keeps working.
"""
import os
from datetime import date

import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
TIMEOUT = 25


def _age(dob_text):
    d, m, y = map(int, dob_text.split("/"))
    today = date.today()
    return today.year - y - ((today.month, today.day) < (m, d))


def _build_prompt(p):
    return (
        "You are a clinical decision-support assistant. Based on the blood test values below, "
        "state the most likely health condition or disease risk (e.g. diabetes risk, anaemia, "
        "high cholesterol / cardiovascular risk), or say values look normal. "
        "Reply in at most 35 words, plain text, no markdown, and end with 'Consult a doctor.'\n\n"
        f"Age: {_age(p['dob'])} years\n"
        f"Glucose: {p['glucose']} mg/dL\n"
        f"Haemoglobin: {p['haemoglobin']} g/dL\n"
        f"Total cholesterol: {p['cholesterol']} mg/dL"
    )


def _rule_based(p):
    notes = []
    g, h, c = p["glucose"], p["haemoglobin"], p["cholesterol"]
    if g >= 200:
        notes.append("very high glucose - possible diabetes")
    elif g >= 126:
        notes.append("high glucose - diabetes risk")
    elif g >= 100:
        notes.append("borderline glucose - pre-diabetes risk")
    if h < 12:
        notes.append("low haemoglobin - possible anaemia")
    elif h > 17.5:
        notes.append("high haemoglobin - possible polycythaemia")
    if c >= 240:
        notes.append("high cholesterol - cardiovascular risk")
    elif c >= 200:
        notes.append("borderline cholesterol")
    body = "; ".join(notes) if notes else "values within normal range"
    return f"[Rule-based fallback] {body}. Consult a doctor."


def get_remarks(patient):
    """Return remark text for a validated patient dict."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return _rule_based(patient)
    try:
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 150,
                "messages": [{"role": "user", "content": _build_prompt(patient)}],
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        text = "".join(b.get("text", "") for b in resp.json().get("content", []))
        return text.strip() or _rule_based(patient)
    except requests.RequestException:
        return _rule_based(patient)
