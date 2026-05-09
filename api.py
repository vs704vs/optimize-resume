from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi import Form
import os
from dotenv import load_dotenv
from groq import Groq
from optimize import read_file, clean_latex_response, MODEL

load_dotenv()

app = FastAPI()

RESUME_PATH = "resume/original/resume.tex"

DEFAULT_SYSTEM_PROMPT = """You are an ATS resume optimizer and LaTeX engineer. Role is software related. Tailor the given LaTeX resume to the job description.

STRICT RULES:
1. Output ONLY valid, compilable LaTeX — no prose, no markdown fences.
2. Preserve all packages, document class, preamble, and structure exactly.
3. Never delete content — only rephrase or add. Every original bullet, keyword, and skill must remain.
4. Mirror JD keywords/terminology naturally in bullets and skills sections.
5. Reorder bullets within each role to lead with the most JD-relevant ones.
6. Add any missing JD keywords into the skills section that don't fit elsewhere.
7. The final resume must fit on a single page. You must be concise: aggressively reword, merge, or shorten points, but do not remove any original information. 
8. Try to keep it concise and mostly one-liner bullet points. Longer or keyword-heavy bullets may become two-liners.
9. Do not try to club together original multiple points into one bullet. You can merge in new content from the JD into existing bullets, but do not remove the original bullet structure or points or any original information or keywords.
10. When rewording, merging, or adding to an existing bullet, ensure the new or modified content is contextually relevant and directly related to the original line. Only add or merge skills, technologies, or responsibilities that are similar or closely related to the original content. Do not add unrelated skills or technologies.
11. Output must compile with pdflatex without errors.
"""

USER_PROMPT_TEMPLATE = """Optimize this LaTeX resume for the job description below.

JOB DESCRIPTION:
{jd}

LATEX RESUME:
{resume}"""



def call_groq(api_key: str, resume: str, jd: str, system_prompt: str) -> str:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": USER_PROMPT_TEMPLATE.format(resume=resume, jd=jd)},
        ],
        temperature=0.3,
        max_tokens=8000,
    )
    return response.choices[0].message.content

@app.post("/optimize", response_class=PlainTextResponse)
async def optimize(
    job_description: str = Form(..., description="Paste the job description here. This will be used to optimize your resume."),
    systemprompt: str = Form("", description="(Optional) Override the default system prompt for resume optimization. Leave blank to use the default.")
):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")
    if not os.path.exists(RESUME_PATH):
        raise HTTPException(status_code=404, detail=f"Resume file not found at {RESUME_PATH}")
    resume = read_file(RESUME_PATH)
    jd = job_description
    # Use default system prompt if blank or only whitespace
    sys_prompt = systemprompt.strip() if systemprompt and systemprompt.strip() else DEFAULT_SYSTEM_PROMPT
    raw_response = call_groq(api_key, resume, jd, sys_prompt)
    optimized_latex = clean_latex_response(raw_response)
    return PlainTextResponse(content=optimized_latex)