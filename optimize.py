#!/usr/bin/env python3
"""
Resume Optimizer — ATS-friendly LaTeX resume tailored to a Job Description
Uses Groq (free tier) + pdflatex to produce a final PDF.

Usage:
    python optimize.py --resume resume.tex --jd jd.txt --output output
"""

import argparse
import os
import subprocess
import sys
import shutil
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   # Best free model on Groq for instruction following

SYSTEM_PROMPT = """You are an ATS resume optimizer and LaTeX engineer. Role is software related.Tailor the given LaTeX resume to the job description.

STRICT RULES:
1. Output ONLY valid, compilable LaTeX — no prose, no markdown fences.
2. Preserve all packages, document class, preamble, and structure exactly.
3. Never delete content — only rephrase or add. Every original bullet and skill must remain.
4. Mirror JD keywords/terminology naturally in bullets and skills sections.
5. Reorder bullets within each role to lead with the most JD-relevant ones.
6. Add any missing JD keywords into the skills section that don't fit elsewhere.
7. The final resume must fit on a single page. You must be concise: aggressively reword, merge, or shorten points, but do not remove any original information. 
8. Try to keep it concise and mostly one-liner bullet points. Only Longer or keyword-heavy bullets may become two-liners.
9. When rewording, merging, or adding to an existing bullet, ensure the new or modified content is contextually relevant and directly related to the original line. Only add or merge skills, technologies, or responsibilities that are similar or closely related to the original content. Do not add unrelated skills or technologies.
10. Output must compile with pdflatex without errors.
"""

USER_PROMPT_TEMPLATE = """Optimize this LaTeX resume for the job description below.

JOB DESCRIPTION:
{jd}

LATEX RESUME:
{resume}"""

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def clean_latex_response(text: str) -> str:
    """Strip any accidental markdown fences the model might add."""
    text = text.strip()
    # Remove ```latex ... ``` or ``` ... ```
    text = re.sub(r"^```(?:latex)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def call_groq(api_key: str, resume: str, jd: str) -> str:
    client = Groq(api_key=api_key)
    print("⏳ Sending to Groq (Llama 3.3 70B)...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT_TEMPLATE.format(resume=resume, jd=jd)},
        ],
        temperature=0.3,      # Low temp = more faithful, less hallucination
        max_tokens=8000,
    )
    return response.choices[0].message.content

def compile_to_pdf_with_pdflatex(latex_source: str, output_name: str) -> str:
    """Compile LaTeX string to PDF using pdflatex from a custom path. Returns the path to the final PDF."""
    import tempfile
    pdflatex_path = os.environ.get("PDFLATEX_PATH")
    if not pdflatex_path:
        print("❌ PDFLATEX_PATH not set in .env file.")
        sys.exit(1)
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)
        print(f"⚙️  Compiling LaTeX → PDF using pdflatex at {pdflatex_path} ...")
        try:
            result = subprocess.run([
                pdflatex_path,
                "-interaction=nonstopmode",
                "resume.tex"
            ], cwd=tmpdir, capture_output=True, text=True, check=True)
            pdf_tmp = os.path.join(tmpdir, "resume.pdf")
            if not os.path.exists(pdf_tmp):
                print("\n❌ Compilation failed. pdflatex output (last 3000 chars):\n")
                print(result.stdout[-3000:])
                print(result.stderr[-3000:])
                sys.exit(1)
            final_pdf = f"{output_name}.pdf"
            shutil.copy(pdf_tmp, final_pdf)
            return os.path.abspath(final_pdf)
        except subprocess.CalledProcessError as e:
            print("Error during PDF generation (pdflatex error):")
            print(e.stdout[-3000:])
            print(e.stderr[-3000:])
            sys.exit(1)
        except FileNotFoundError:
            print(f"Could not find pdflatex at {pdflatex_path}. Please check the path.")
            sys.exit(1)


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Paste your job description here as a string (multi-line allowed)
    JOB_DESCRIPTION = """
About the Role

This role involves building and maintaining robust backend systems, solving real-world technical challenges, and optimizing performance. It requires strong foundations in clean coding practices, peer reviews, and agile development. Best suited for someone who values ownership, quality, and adaptability in a high-performance environment.



What We Expect From You



Key Responsibilities

Implement assigned features and changes through performant and maintainable code, with appropriate test coverage (unit, contract, component).
Understand the design and architecture of the component/service and implement low-level designs (LLDs) following best practices.
Perform effective code reviews for peers.
Consider customer experience and product performance in implementation.
Develop awareness of how your work impacts key product metrics.
Handle on-call responsibilities effectively within the team.
Contribute to RCA discussions and support RCA documentation.
Proactively gather and understand requirements for assigned features.
Ask questions, clarify uncertainties, and document requirements accurately.
Collaborate effectively with developers in the team to implement features with quality.


Must Haves

Proficiency in at least one of the following languages: Java, Go, or Kotlin
Solid understanding of object-oriented design, design patterns, and data structures
Experience in implementing algorithms to solve real-world problems
Proven track record in building and maintaining backend systems
Ability to troubleshoot and optimize backend systems for better performance
Learn and contribute to distributed system design under mentorship.
Demonstrated expertise in unit testing, peer code reviews, and familiarity with agile methodologies
Good verbal and written communication and interpersonal skills
A history of delivering on-time with a focus on quality output
Emphasis on observability, ensuring systems are well-monitored and maintainable
At least 1+ years of software development experience


Preferred Skills

Familiarity with event-driven architectures and messaging systems (e.g., Kafka, RabbitMQ)
Knowledge of security best practices for backend services and API endpoints
Ability to quickly adapt to new and complex development environments
Strong analytical skills with the ability to deep dive into technical challenges
    """

    JOB_TITLE = "SDE1(Backend)"  # Set your job title here
    COMPANY_NAME = "Navi"      # Set your company name here


    parser = argparse.ArgumentParser(description="ATS Resume Optimizer")
    parser.add_argument("--resume", required=False, default="resume/original/resume.tex", help="Path to your resume.tex (default: resume/original/resume.tex)")
    parser.add_argument("--output", default=None, help="Output filename (without extension)")
    parser.add_argument("--key",    default=None,   help="Groq API key (or set GROQ_API_KEY env var)")
    parser.add_argument("--save-tex", action="store_true", help="Also save the intermediate .tex file")
    args = parser.parse_args()

    # ── API key
    api_key = args.key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ No Groq API key found.")
        print("   Set it via:  export GROQ_API_KEY=your_key_here")
        print("   Or pass it:  --key your_key_here")
        print("   Get a free key at: https://console.groq.com")
        sys.exit(1)


    if not os.path.exists(args.resume):
        print(f"❌ Resume file not found: {args.resume}")
        sys.exit(1)

    # Ensure output directory exists
    output_dir = "resume"
    os.makedirs(output_dir, exist_ok=True)

    # ── Read inputs
    resume = read_file(args.resume)
    jd     = JOB_DESCRIPTION
    print(f"✅ Loaded resume : {args.resume} ({len(resume)} chars)")
    print(f"✅ Loaded JD     : (from variable, {len(jd)} chars)")

    # ── Call AI
    raw_response = call_groq(api_key, resume, jd)
    optimized_latex = clean_latex_response(raw_response)
    print(f"✅ Got optimized LaTeX ({len(optimized_latex)} chars)")

    # ── Optionally save .tex
    if args.save_tex:
        tex_out = os.path.join(output_dir, f"Vishal_Sharma_{JOB_TITLE}_{COMPANY_NAME}.tex")
        with open(tex_out, "w", encoding="utf-8") as f:
            f.write(optimized_latex)
        print(f"💾 Saved LaTeX to : {tex_out}")

    # ── Compile to PDF
    output_pdf_name = args.output or f"Vishal_Sharma_{JOB_TITLE}_{COMPANY_NAME}"
    output_pdf_path = os.path.join(output_dir, output_pdf_name)
    pdf_path = compile_to_pdf_with_pdflatex(optimized_latex, output_pdf_path)
    print(f"\n🎉 Done! PDF saved to: {pdf_path}")
if __name__ == "__main__":
    main()
