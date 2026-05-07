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
import tempfile
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   # Best free model on Groq for instruction following

SYSTEM_PROMPT = """You are an expert ATS resume optimizer and LaTeX engineer.
Your job is to modify a LaTeX resume so it is tailored to a specific job description.

STRICT RULES:
1. Return ONLY the complete, valid, compilable LaTeX — no explanations, no markdown fences, no commentary.
2. Preserve ALL LaTeX packages, document class, preamble, and overall structure exactly.
3. Do NOT remove any bullet points, skills, or details from the original resume. You may rephrase or add, but never delete existing content.
5. Mirror keywords, phrases, and terminology from the job description naturally in bullet points and skills.
7. Reorder bullet points within each position to surface the most relevant ones first, based on the job description.
8. Rephrase existing bullet points to use JD's language where a close match exists, but keep the original meaning and details intact.
9. In the skills/technologies section, add any missing keywords from the JD that do not fit elsewhere, so that all JD keywords appear somewhere in the resume.
10. You may add new bullet points or skills to ensure all JD keywords are present
11. The resume should be enhanced, not reduced.
12. Keep the resume length the same do not remove sections or points.
13. The output must compile with pdflatex without errors.
"""

USER_PROMPT_TEMPLATE = """Optimize the LaTeX resume below for the following job description.

═══════════════════════════════
JOB DESCRIPTION
═══════════════════════════════
{jd}

═══════════════════════════════
LATEX RESUME
═══════════════════════════════
{resume}

Now return the fully optimized LaTeX resume. Remember: ONLY LaTeX code, nothing else."""

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
                "resume.tex"
            ], cwd=tmpdir, capture_output=True, text=True, check=True)
            pdf_tmp = os.path.join(tmpdir, "resume.pdf")
            if not os.path.exists(pdf_tmp):
                print("\n❌ Compilation failed. pdflatex output:\n")
                print(result.stdout[-3000:])
                print(result.stderr[-3000:])
                sys.exit(1)
            final_pdf = f"{output_name}.pdf"
            shutil.copy(pdf_tmp, final_pdf)
            return os.path.abspath(final_pdf)
        except subprocess.CalledProcessError as e:
            print("Error during PDF generation:")
            print(e.stdout)
            print(e.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"Could not find pdflatex at {pdflatex_path}. Please check the path.")
            sys.exit(1)


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Paste your job description here as a string (multi-line allowed)
    JOB_DESCRIPTION = """
    About This Role

Wells Fargo is seeking a Software Engineer

In This Role, You Will

Participate in low to moderately complex initiatives and projects associated with the technology domain, including installation, upgrades, and deployment efforts
Identify opportunities for service quality and availability improvements within the technology domain environment
Design, code, test, debug, and document for low to moderately complex projects and programs associated with technology domain, including upgrades and deployments
Review and analyze technical assignments or challenges that are related to low to medium risk deliverables and that require research, evaluation, and selection of alternative technology domains
Present recommendations for resolving issues or may escalate issues as needed to meet established service level agreements
Exercise some independent judgment while also developing understanding of given technology domain in reference to security and compliance requirements
Provide information to technology colleagues, internal partners, and stakeholders

Required Qualifications:

2+ years of software engineering experience, or equivalent demonstrated through one or a combination of the following: work experience, training, military experience, education

Desired Qualifications:

Experience in Software Engineering, or equivalent demonstrated through one or a combination of the following: work experience, training, military experience, education
Hands-on experience with agentic architectures, frameworks, or platforms like LangChain, LangGraph, OpenAI Agents or similar.
Practical experience designing, developing, or deploying agentic systems (autonomous agents, AI-powered assistants, workflow automation agents, or multi-agent frameworks.
Demonstrated proficiency in software applications and technical processes within a technical discipline cloud, artificial intelligence, machine learning, mobile frontend development etc.
Experience in the Cloud technologies like OpenShift /PCF etc.
Proficiency in developing web-based applications, should have experience in UI/frontend and Server technologies (ANGULAR / React, Spring Framework, JDBC, JavaBeans).
Experience in developing client-side UI components using Angular / React.
Experience in developing the functionalities, enhancements, and bug fixes for application (UI/Backend) by consuming and exposing services.
Designing, implementing, and maintaining Java services with well-designed, efficient, and test-driven code.
Experience in Developing Restful Web services and Micro services in java by using Spring boot.
Develop service/business layer components using Spring and EJBS.
Should be able to design and develop MVC restful services using JAVA spring boot (MVC) with Oracle/SQL Server Database.
Strong knowledge of Junit/TestNG, Selenium frameworks and test automation.
Design cross platform consumption patterns, microservices, and event-driven architectures for high availability and scalability.
Experience with Autosys similar orchestration tools.
Working knowledge of REST APIs, Object Storage, and CI/CD pipelines

Job Expectations:

Involve in end -end lifecycle of Product/Application development, analyze highly complex business requirements, designs and writes technical specifications to design or redesign complex modules and applications.
Expand digital client experiences by leveraging AI and Machine learning, and Agentic capabilities..
leverage AI to Identify and automate remediation of recurring issues to improve operational stability.
Utilize AI SDLC toolset like story weaver, MCP tools to support development, develop secure high quality production code.
Develop highly complex original code and provide coding direction to junior team members
Proficiency with Agile, DevOps practices, delivering Cloud solutions. Experience with delivering projects using Agile software development techniques.
Advanced knowledge of object-oriented design and development (OOA/OOD) and the JAVA patterns and practices
Must possess innovative and Out-of-box thinking while developing advanced technical solutions to business problems and grab opportunities to improve system resiliency.
Collaborate with cross-functional teams to build scalable, high-performance cloud native solutions using Java, Python, microservices, and Autosys.

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
