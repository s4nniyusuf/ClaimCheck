# ClaimCheck

> Does this seller deliver what they promise?

ClaimCheck compares what sellers claim in their product descriptions against what customers actually experience in their reviews, so you can verify your next purchase before placing an order.

Beyond helping buyers decide, ClaimCheck pushes sellers toward transparency and accountability.

Built for the Nigerian e-commerce market where "what I ordered vs what I got" is still one of the most common frustrations on platforms like Jumia.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-59666C?style=for-the-badge&logo=python&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## The Problem

Nigeria's e-commerce market is projected to reach $18B by 2030. But behind that growth, millions of buyers still receive products that don't match their expectations. Sellers write descriptions that sound great, but reviews tell a different story.

ClaimCheck bridges that gap.

---

## How It Works

```
Paste any Jumia product URL
              ↓
Scrape product name, description, rating and reviews
              ↓
Extract every claim the seller makes
              ↓
Run aspect-based sentiment analysis on customer reviews
              ↓
Compare seller claims against real customer experiences
              ↓
Generate a clear breakdown with trust scores and verdicts
```

---

## Features

**Aspect Verdict Cards**
Every product aspect the seller describes gets its own card showing their exact claims, real customer sentiments, and a verdict on whether it holds up.

**Four verdicts:**
- ✓ `CONFIRMED` — customers back the claim
- `~` `MIXED` — customers are split
- `?` `UNVERIFIED` — not enough review data to judge
- `✕` `CONTRADICTED` — customers say otherwise

**Trust Score**
A 0–100 score computed from all verified aspect verdicts — weighted by how strongly each verdict is supported.

**Unclaimed Aspects**
The most unique feature. ClaimCheck surfaces aspects sellers never mention in their descriptions but customers repeatedly bring up in reviews, whether it's a flaw they're hiding or a strength they forgot to mention.

**Confidence-weighted verdicts**
A single negative review can't contradict a seller claim. ClaimCheck requires a minimum of 2 reviews per aspect and a 75% sentiment majority before committing to a verdict — making the output trustworthy rather than reactive.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Scraping | Playwright + BeautifulSoup |
| NLP preprocessing | spaCy |
| LLM inference | Groq (`llama-3.3-70b-versatile`) |
| Frontend | Streamlit |
| Language | Python 3.11+ |

---

## Project Structure

```
claim_check/
├── .streamlit/ 
│      └── config.toml                      # Streamlit theme and configuration
│
├── prompts/
│   ├── __init__.py
│   ├── extract_sellers_claim_prompt.py     # Prompt for extracting seller claims from descriptions
│   ├── grammar_fix_prompt.py               # Prompt for cleaning and fixing description grammar
│   └── review_analysis_prompt.py           # Prompt for running aspect-based sentiment analysis
│
├── src/
│      ├── app.py                           # Streamlit UI and application entry point
│      ├── comparator.py                    # Compares seller claims against customer sentiments
│      ├── extractor.py                     # Extracts seller claims and runs sentiment analysis on reviews
│      └── scraper.py                       # Scrapes product details and reviews from Jumia
│
├── .gitignore                              # Files and folders excluded from version control
├── .python-version                         # Pinned Python version managed by uv
├── LICENSE                                 # MIT License
├── pyproject.toml                          # Project metadata and dependencies
├── README.md                               # Project documentation
└── uv.lock                                 # Dependency lockfile
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/s4nni_yusuf/claimcheck.git
```
```bash
cd claimcheck
```

**2. Install dependencies**
```bash
uv sync
```

**3. Install Playwright browser**
```bash
uv run playwright install chromium
```

**4. Install spaCy language model**
```bash
uv run python -m spacy download en_core_web_sm
```

**5. Set up your environment variables**
```bash
touch .env
```
Add this inside:
```
GROQ_API_KEY_1=your_groq_api_key_here
```

You can get a free Groq API key at [console.groq.com](https://console.groq.com).

**6. Run the app**
```bash
uv run streamlit run src/app.py
```

---


## Live Demo

[claimcheck.streamlit.app](https://claimcheck.streamlit.app)

---

## Feedback

Especially welcome from anyone who's been humbled by a bad Jumia order.

Open an issue, submit a PR, or reach out on X [@s4nni_yusuf](https://x.com/s4nni_yusuf).

If you find ClaimCheck useful, consider giving it a star ⭐. it helps more people find the project.

---

## License

MIT
