from threading import Lock
import re
import requests
from decouple import config

MODEL_LOCK = Lock()

GEMINI_API_KEY = config("GEMINI_API_KEY", default=None)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key="

def query_gemini(prompt):
    if not GEMINI_API_KEY:
        return ""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL + GEMINI_API_KEY, json=payload, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error {response.status_code}: {response.text}")

        result = response.json()
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return ""
    except Exception as e:
        print(f"Gemini Query failed: {e}")
        return ""


def generate_subtasks(main_task, max_subtasks=7):

    fallback_subtasks = [
        {"name": f"Understand: {main_task}", "status": "pending"},
        {"name": "Break into steps", "status": "pending"},
        {"name": "Gather requirements", "status": "pending"},
        {"name": "Execute task", "status": "pending"},
        {"name": "Review output", "status": "pending"},
    ]

    if not GEMINI_API_KEY:
        return {
            "main_task": main_task,
            "sub_tasks": fallback_subtasks[:max_subtasks]
        }

    prompt = f"""
Break this task into simple steps.

Task: {main_task}

Rules:
- Return ONLY a numbered list
- Each step should be short and actionable
- No explanations
"""

    try:
        with MODEL_LOCK:
            text = query_gemini(prompt)

        subtasks = []
        seen = set()

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            # clean numbering/bullets
            line = re.sub(r"^[-•*\s]*\d*[\.\)]?\s*", "", line).strip()

            if len(line.split()) < 2:
                continue

            if main_task.lower() in line.lower():
                continue

            key = line.lower()
            if key in seen:
                continue
            seen.add(key)

            subtasks.append({
                "name": line,
                "status": "pending"
            })

        if not subtasks:
            subtasks = fallback_subtasks

        return {
            "main_task": main_task,
            "sub_tasks": subtasks[:max_subtasks]
        }

    except Exception as e:
        print("HF Error:", e)
        return {
            "main_task": main_task,
            "sub_tasks": fallback_subtasks[:max_subtasks],
            "error": str(e)
        }