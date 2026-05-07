# Resume Optimizer — ATS-Ready PDF from LaTeX

Takes your LaTeX resume + a job description → produces an ATS-optimized PDF.
Uses **Groq's free API** (Llama 3.3 70B) + **Tectonic** (free, local, cross-platform LaTeX engine).

---

## 1. One-Time Setup

### A. Install Python dependencies
```bash
pip install -r requirements.txt
```


### B. Install Tectonic (LaTeX engine)

**Windows (recommended):**
```bash
winget install tectonic
```

**macOS:**
```bash
brew install tectonic
```

**Linux:**
```bash
cargo install tectonic
# or see https://tectonic-typesetting.github.io/en-US/install.html
```


### C. Get a free Groq API key
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create an API key
4. Add it to a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Alternatively, you can set the key as an environment variable or pass it with `--key`.

---

## 2. Usage


### Basic usage
1. Place your LaTeX resume as `resume.tex` and the job description as `jd.txt` in the project root (same folder as `optimize.py`).
2. Run:
	```bash
	python optimize.py --resume resume.tex --jd jd.txt
	```
	This produces: `optimized_resume.pdf` in the same folder.

### Custom output name
```bash
python optimize.py --resume resume.tex --jd jd.txt --output google_resume
```
Produces: `google_resume.pdf`

### Also keep the .tex file (useful for manual tweaks)
```bash
python optimize.py --resume resume.tex --jd jd.txt --output google_resume --save-tex
```
Produces: `google_resume.pdf` + `google_resume.tex`

### Pass API key inline (if you haven't set .env or env var)
```bash
python optimize.py --resume resume.tex --jd jd.txt --key gsk_xxxxx
```

---

## 3. Tips for Best Results

- **JD file**: Paste the full job description as plain text into `jd.txt`. The more complete, the better.
- **Your resume**: Keep it as a single `.tex` file. Multi-file setups (with `\input{}`) need to be merged first.
- **Review before sending**: The AI won't fabricate experience, but always read the output — rephrasings should sound like you.
- **Compilation errors**: Run with `--save-tex` and open the `.tex` in Overleaf to debug any LaTeX issues.

---

## 4. Free Tier Limits

| Service | Limit | Enough? |
|---------|-------|---------|
| Groq    | ~14,400 req/day | ✅ Yes — each resume edit = 1 request |
| Tectonic | Unlimited (local) | ✅ Yes |

You can optimize your resume **dozens of times per day** without hitting any limits.

---

## 5. File Structure

```
resume_optimizer/
├── optimize.py        ← main script
├── requirements.txt   ← pip dependencies
├── README.md
├── .env               ← your Groq API key (you add this)
├── resume.tex         ← your base resume (you add this)
└── jd.txt             ← job description (you add this each time)
```
