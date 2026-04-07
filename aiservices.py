from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# ✅ LOAD ENV VARIABLES FIRST
load_dotenv()

# ✅ GET API KEY
api_key = os.getenv("OPENAI_API_KEY")

# Debug (you can remove later)
print("Loaded API KEY:", api_key)

# ❗ Handle missing key safely
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

# ✅ CREATE CLIENT
client = OpenAI(api_key=api_key)


def generate_ai(description):

    prompt = f"""
    You are a welding expert.

    Project: {description}

    Return ONLY valid JSON:
    {{
      "time": "estimated time",
      "steps": ["step1", "step2"],
      "safety": ["rule1", "rule2"],
      "alternatives": ["alt1", "alt2"]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content

        # ✅ Try parsing AI response
        return json.loads(content)

    except Exception as e:
        print("AI ERROR:", e)

        # ✅ FALLBACK (VERY IMPORTANT)
        return {
            "time": "2-4 hours (estimated)",
            "steps": [
                "Measure materials",
                "Cut metal pieces",
                "Weld joints together",
                "Grind and finish surface"
            ],
            "safety": [
                "Wear welding mask",
                "Use gloves",
                "Ensure proper ventilation"
            ],
            "alternatives": [
                "Use aluminum instead of steel",
                "Use bolting instead of welding"
            ]
        }