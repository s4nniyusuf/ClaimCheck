import re
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import spacy
from groq import Groq
from dotenv import load_dotenv

from prompts.grammar_fix_prompt import grammar_fix_prompt
from prompts.extract_sellers_claim_prompt import extract_seller_claims_prompt
from prompts.review_analysis_prompt import review_analysis_prompt

nlp = spacy.load("en_core_web_sm")

load_dotenv(override=False)

def _get_key(name: str) -> str:
    key = os.getenv(name)
    if not key:
        raise ValueError(f"{name} is not set. Provide it as an environment variable.")
    return key

client = Groq(api_key=_get_key("GROQ_API_KEY"))


def preprocess_description(text: str) -> str:
    """Cleans product descriptions by standardizing whitespace, fixing formatting,
    and removing duplicate sentences."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)
    text = text.replace('\xa0', ' ')

    seen = set()
    unique = []
    doc = nlp(text)
    for sent in doc.sents:
        normalized = sent.text.strip().lower()
        if not normalized:
            continue
        if normalized not in seen:
            seen.add(normalized)
            unique.append(sent.text.strip())

    return " ".join(unique)


def fix_description_grammar(description: str) -> str:
    """Fix grammar, punctuation, and run-on sentences without changing any claims."""
    try:
        content = grammar_fix_prompt.replace("{description}", description)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": content}],
            temperature=0.1
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Error fixing grammar:", e)
        return description  # fall back to input


def extract_sellers_claim_from_description(description: str) -> list[dict]:
    """Extracts seller claims from the cleaned description and returns them as a list of dicts."""
    try:
        content = extract_seller_claims_prompt.replace("{description}", description)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        raw = chat_completion.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"Failed to parse model response as JSON: {e}")
        return []
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return []


def extract_seller_claims(description: str) -> list[dict]:
    if not description or description.strip() == "N/A":
        print("No description to extract claims from.")
        return []
    preprocessed_description = preprocess_description(text=description)
    cleaned_description = fix_description_grammar(description=preprocessed_description)
    return extract_sellers_claim_from_description(description=cleaned_description)


def extract_aspect_and_sentiment_from_review(review_text: str) -> dict:
    """Extracts aspects and their sentiment from a review and returns them as a dict."""
    try:
        content = review_analysis_prompt.replace("{review_text}", review_text)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": content}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"Failed to parse model response as JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error extracting aspect and sentiment: {e}")
        return {}


def analyze_reviews(reviews: list) -> list[dict]:
    if not reviews:
        print("No reviews to analyze.")
        return []
    results = []
    for review in reviews:
        aspect_and_sentiment = extract_aspect_and_sentiment_from_review(review_text=review)
        results.append({
            "review": review,
            "aspect_and_sentiment": aspect_and_sentiment
        })
    return results