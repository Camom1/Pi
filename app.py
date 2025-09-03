# app.py
import os
from pathlib import Path
from flask import Flask, request, render_template

# ===== Resolve paths relative to this file =====
BASE_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = BASE_DIR / "templates"

# ===== OpenAI setup (optional for now) =====
OPENAI_API_KEY = "APIKEY"
if not OPENAI_API_KEY:
    print("⚠️ WARNING: OPENAI_API_KEY no está configurada")

# Intenta usar el nuevo SDK, si no el viejo
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    USE_NEW_SDK = True
except ImportError:
    import openai
    openai.api_key = OPENAI_API_KEY
    client = None
    USE_NEW_SDK = False
# ===== Flask app, explicitly bind templates dir =====
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

@app.route("/", methods=["GET", "POST"])
def index():
    prompt = result = error = None

    if request.method == "POST":
        # Leer campos del formulario
        name        = (request.form.get("name") or "").strip()
        ideal_role  = (request.form.get("ideal_role") or "").strip()

        if not name or not ideal_role:
            error = "Please provide at least your full name and ideal role."
            return render_template("index.html", prompt=prompt, result=result, error=error)
             
        if not OPENAI_API_KEY:
            error = "Missing OPENAI_API_KEY environment variable."
            return render_template("index.html", prompt=prompt, result=result, error=error)

        prompt = f"""
You are Pathwise, an expert career planner. Using the candidate info below, produce a clear 5-step career roadmap that logically progresses toward the ideal role: {ideal_role}.

Candidate:
- Name: {name}
- Work Experience: {(request.form.get("work_experience") or "N/A").strip()}
- Education: {(request.form.get("education") or "N/A").strip()}
- Technical Skills: {(request.form.get("tech_skills") or "N/A").strip()}
- Soft Skills: {(request.form.get("soft_skills") or "N/A").strip()}
- Languages: {(request.form.get("languages") or "N/A").strip()}
- Availability & Preferences: {(request.form.get("preferences") or "N/A").strip()}

Instructions:
- Output 5 sequential roles (Step 1 → Step 5) with:
  • Brief role description (2 or 3 lines)
  • Key skills/experience required
  • Recommended courses/certifications (concrete, recognizable options)
  • Why this step moves the candidate closer to the ideal role
- Keep it concise, actionable, and tailored to the candidate.
- At Step 5, ensure the candidate is fully ready to perform as a {ideal_role}.
""".strip()

        try:
            if USE_NEW_SDK and client:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=700,
                    temperature=0.4,
                )
                result = resp.choices[0].message.content.strip()
            else:
                resp = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=700,
                    temperature=0.4,
                )
                result = resp.choices[0].message["content"].strip()
        except Exception as e:
            error = f"OpenAI error: {e}"

    return render_template("index.html", prompt=prompt, result=result, error=error)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)




