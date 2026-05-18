## [claim_check]()

---

### Project Description

---

### Project Structure

```
claim_check/
├── .streamlit/ 
│      └── config.toml                      # Streamlit configs
│
├── prompts
│   ├── __init__.py
│   ├── extract_sellers_claim_prompt.py     # Prompt for extracting seller claims
│   ├── grammar_fix_prompt.py               # Prompt for grammar fixes
│   └── review_analysis_prompt.py           # Prompt for review analysis
│
├── src/
│      ├── app.py                           # Main application entry point
│      ├── comparator.py                    # Claim comparison module
│      ├── extractor.py                     # Data extraction module
│      └── scraper.py                       # Jumia Scraping Module
│
├── .gitignore                              # Ignore unnecessary files
├── .python-version                         # Pinned Python version (managed by uv)
├── LICENSE                                 # MIT License
├── pyproject.toml                          # Project metadata and dependencies
├── README.md                               # This file
└── uv.lock                                 # Lockfile

```
---

### How it works 

---

### Technical Stack 
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)

---

### How to Run Locally

1. **Clone the repo**
    ```bash
        https://github.com/s4nniyusuf/claim_check.git    
    ```
    ```bash
        cd claim_check
    ```

2. **Install dependencies**
    ```bash
        uv sync
    ```

3. **Set up environment variables**. Create a `.env` file in the root directory:

4. **Run the app**
    ```bash
        streamlit run src/app.py
    ```
    
---

### Futher Improvement
