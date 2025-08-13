# app.py
import os
from pathlib import Path
from flask import Flask, request, render_template

# ===== Resolve paths relative to this file =====
BASE_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = BASE_DIR / "templates"

# ===== OpenAI setup (optional for now) =====
OPENAI_API_KEY = "sk-proj-Rmugg4wxH2WeBoIVFUZLT3BlbkFJtllecELQncBwnGnMLiKQ"
USE_NEW_SDK = False
client = None
try:
    from openai import OpenAI  # new SDK
    client = OpenAI(api_key=OPENAI_API_KEY)
    USE_NEW_SDK = True
except Exception:
    try:
        import openai  # legacy SDK
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
    except Exception:
        openai = None  # type: ignore

# ===== Flask app, explicitly bind templates dir =====
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

# Helpful diagnostics that work with Flask 3
print("RUNNING FILE:", __file__)
print("CWD (os.getcwd()):", os.getcwd())
print("app.root_path:", app.root_path)
print("app.template_folder:", app.template_folder)
print("Expected template path:", TEMPLATES_DIR / "index.html")
print("Template exists?:", (TEMPLATES_DIR / "index.html").exists())

@app.route("/", methods=["GET", "POST"])
def index():
    print("Hitting / route")
    prompt = None
    result = None
    error = None

    if request.method == "POST":
        # Read survey fields from the form
        name        = (request.form.get("name") or "").strip()
        ideal_role  = (request.form.get("ideal_role") or "").strip()
        work_exp    = (request.form.get("work_experience") or "").strip()
        education   = (request.form.get("education") or "").strip()
        tech_skills = (request.form.get("tech_skills") or "").strip()
        soft_skills = (request.form.get("soft_skills") or "").strip()
        languages   = (request.form.get("languages") or "").strip()
        preferences = (request.form.get("preferences") or "").strip()

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
- Work Experience: {work_exp or "N/A"}
- Education: {education or "N/A"}
- Technical Skills: {tech_skills or "N/A"}
- Soft Skills: {soft_skills or "N/A"}
- Languages: {languages or "N/A"}
- Availability & Preferences: {preferences or "N/A"}

Instructions:
- Output 5 sequential roles (Step 1 → Step 5) with:
  • Brief role description (2–3 lines)
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
                if "openai" not in globals() or openai is None:
                    raise RuntimeError("OpenAI SDK not installed. Run: pip install openai")
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
    # Fixed host/port; disable reloader so you always hit THIS file
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)




