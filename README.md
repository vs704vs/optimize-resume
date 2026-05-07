# Resume Optimizer — ATS-Ready PDF from LaTeX

Takes your LaTeX resume + a job description → produces an ATS-optimized PDF.
Uses **Groq's free API** (Llama 3.3 70B) + **MiKTeX's pdflatex** (local, Windows, or any pdflatex you provide).

---

## 1. One-Time Setup

### A. Install Python dependencies
```bash
pip install -r requirements.txt
```



### B. Install MiKTeX (or any pdflatex)

**Windows:**
Download and install MiKTeX from https://miktex.org/download
Find the path to `pdflatex.exe` (e.g. `D:/proj/resume_optimizer/MiKTeX/installed/miktex/bin/x64/pdflatex.exe`)

**macOS/Linux:**
Install TeX Live or another LaTeX distribution that provides `pdflatex` and set its path in the `.env` file.


### C. Get a free Groq API key
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create an API key
4. Add it to a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
PDFLATEX_PATH=D:/proj/resume_optimizer/MiKTeX/installed/miktex/bin/x64/pdflatex.exe
```

Alternatively, you can set the key as an environment variable or pass it with `--key`. The `PDFLATEX_PATH` must be set in `.env` or your environment.

---

## 2. Usage


### Basic usage

1. Place your LaTeX resume as `resume.tex` in the project root (same folder as `optimize.py`).
2. Open `optimize.py` and paste your job description string into the `JOB_DESCRIPTION` variable at the top of the `main()` function.
3. Run:
   ```bash
   python optimize.py --resume resume.tex
   ```
   This produces: `optimized_resume.pdf` in the same folder.

### Custom output name

```bash
python optimize.py --resume resume.tex --output google_resume
```
Produces: `google_resume.pdf`

### Also keep the .tex file (useful for manual tweaks)

```bash
python optimize.py --resume resume.tex --output google_resume --save-tex
```
Produces: `google_resume.pdf` + `google_resume.tex`

### Pass API key inline (if you haven't set .env or env var)

```bash
python optimize.py --resume resume.tex --key gsk_xxxxx
```

---

## 3. Tips for Best Results


- **Job Description**: Paste your job description as a string in the `JOB_DESCRIPTION` variable in `optimize.py`.
- **Your resume**: Keep it as a single `.tex` file. Multi-file setups (with `\input{}`) need to be merged first.
- **Review before sending**: The AI will not remove any of your original points, only add or rephrase for ATS. Always review the output.
- **ATS Optimization**: All keywords from the job description will be present in your resume, either in the relevant section or in the skills section if they don't fit elsewhere.
- **Compilation errors**: Run with `--save-tex` and open the `.tex` in Overleaf to debug any LaTeX issues.

---

## 4. Free Tier Limits

| Service | Limit | Enough? |
|---------|-------|---------|
| Groq    | ~14,400 req/day | ✅ Yes — each resume edit = 1 request |
| pdflatex | Unlimited (local) | ✅ Yes |

You can optimize your resume **dozens of times per day** without hitting any limits.

---

## 5. File Structure

```
resume_optimizer/
├── optimize.py        ← main script
├── requirements.txt   ← pip dependencies
├── README.md
├── .env               ← your Groq API key and pdflatex path (you add this)
├── resume.tex         ← your base resume (you add this)
```
