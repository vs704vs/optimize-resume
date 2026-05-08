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
8. Try to keep it concise. Longer or keyword-heavy bullets may become two-liners.
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
Job Description

What You'll Do:

Develop and maintain applications using Golang or Java, following clean code and best software engineering practices.
Design and implement scalable, reliable, and secure microservices architecture.
Collaborate with engineering and product teams to refine and deliver technical solutions aligned with business needs.
Leverage AWS services such as SQS, SNS, DynamoDB, S3, and EventBridge in day-to-day development.
Use Terraform to provision, maintain, and evolve AWS infrastructure.
Write unit and integration tests to ensure code quality and system robustness.
Monitor application health and performance using observability tools (metrics, logs, alerts).
Participate in code reviews and provide constructive feedback to peers.
Contribute to architectural and technical discussions, supporting continuous improvement and innovation
High-Impact Contributions: Regularly recognized for delivering high-quality, impactful technical solutions within their team and across collectives. Coding Standards & Best Practices: Actively enables other engineers to elevate coding standards and deepen awareness of best practices, especially around non-functional requirements. Technical Leadership: Consistently leads their squad to successful technical outcomes, ensuring sound engineering decisions that balance technical debt, system design, reliability, observability, and business needs. Product Awareness & Planning: Demonstrates strong product understanding, contributes meaningfully to quarterly planning, and collaborates with PMs or team leads to shape squad vision. Mentorship & Feedback: Proactively supports the growth of other engineers through mentoring, sponsorship, and constructive feedback. Cross-Team Collaboration: Frequently consulted by engineers from other squads, demonstrating the ability to tackle complex and ambiguous problems under pressure. Technology Strategy: Keeps up with emerging technology trends and contributes insights to squad-level strategic discussions.

  This is a remote position. A remote position does not require job duties be performed within proximity of a Visa office location. Remote positions may be required to be present at a Visa office with scheduled notice. 


Visa requires at least 3 days in office, expectations of these days will be confirmed by your Hiring Manager.
Qualifications

Basic Qualifications:
Bachelor's degree, OR 6 months to 2 years of relevant work experience

Preferred Qualifications:
Bachelor's degree, OR 6 months to 2 years of relevant work experience
proficiency in years of experience with Golang
Adaptable to other languages like - Java/Groovy or JVM-related.
Solid knowledge of AWS Services or other Cloud Players
Knowledge of Distributed transactions and Race Conditions
Experience/knowledge with Continuous Integration & Development and automation tools such as Jenkins, CodeFresh, ArgoCD, Artifactory, Git etc.
Solid knowledge and understanding of Agile and Test-Driven Development
Deep product knowledge, active in feature planning and impact analysis.
Strong relational database design and non-relational strategy, effective data modelling.
Experience with Financial Industry or Payments / Authorization Systems.
Understanding of observability practices (monitoring, tracing, alerting).
    """

    parser = argparse.ArgumentParser(description="ATS Resume Optimizer")
    parser.add_argument("--resume", required=True,  help="Path to your resume.tex")
    parser.add_argument("--output", default="optimized_resume", help="Output filename (without extension)")
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
        tex_out = f"{args.output}.tex"
        with open(tex_out, "w", encoding="utf-8") as f:
            f.write(optimized_latex)
        print(f"💾 Saved LaTeX to : {tex_out}")

    # ── Compile to PDF
    pdf_path = compile_to_pdf_with_pdflatex(optimized_latex, args.output)
    print(f"\n🎉 Done! PDF saved to: {pdf_path}")
if __name__ == "__main__":
    main()
