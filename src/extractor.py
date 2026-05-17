import re
import os
import sys
import json
# Add the parent directory to sys.path to allow imports from the prompts package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import spacy
from groq import Groq
from dotenv import load_dotenv

from prompts.grammar_fix_prompt import grammar_fix_prompt
from prompts.extract_sellers_claim_prompt import extract_seller_claims_prompt
from prompts.review_analysis_prompt import review_analysis_prompt


nlp = spacy.load("en_core_web_sm")

def load_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY_1")
    return api_key


def preprocess_description(text: str) -> str:
  """Cleans product descriptions by standardizing whitespace, fixing formatting, and removing duplicate sentences."""

  # normalise white space
  text = re.sub(r'\s+', ' ', text)

  # Inserts a period when a lowercase letter is immediately followed by an uppercase letter
  text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)

  # Replaces the Unicode non-breaking space with a normal space
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
    """
    Fix grammar, punctuation, and run-on sentences in a product description
    without changing any claims.
    """

    try:
        api_key = load_api_key()
        client = Groq(api_key=api_key)

        content = grammar_fix_prompt.replace("{description}", description)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or your preferred model
            messages=[{"role": "user", "content": content}]
        )

        fixed_text = response.choices[0].message.content
        print(fixed_text)
        return fixed_text

    except Exception as e:
        print("Error fixing grammar:", e)
        return None


def extract_sellers_claim_from_description(description: str) -> list[dict]:
    """Extracts seller claims from the cleaned description and returns them as a list of dicts."""
    try:
        api_key = load_api_key()
        client2 = Groq(api_key=api_key)

        content = extract_seller_claims_prompt.replace("{description}", description)

        chat_completion = client2.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama-3.3-70b-versatile",
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


def extract_seller_claims(description):
   preprocessed_description = preprocess_description(text=description)
   cleaned_description = fix_description_grammar(description=preprocessed_description)
   seller_claims = extract_sellers_claim_from_description(description=cleaned_description)

   print(seller_claims)
   return seller_claims


def extract_aspect_and_sentiment_from_review(review_text: str) -> dict:
    """Extracts aspects and their sentiment from a review and returns them as a dict."""
    try:
        api_key = load_api_key()
        client = Groq(api_key=api_key)

        content = review_analysis_prompt.replace("{review_text}", review_text)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": content}]
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
    
    
def analyze_reviews(reviews: list):
    results = []
    for review in reviews:
      aspect_and_sentiment = extract_aspect_and_sentiment_from_review(review_text=review)
      results.append(
         {"review": review, 
          "aspect_and_sentiment": aspect_and_sentiment}
      )
    print(results)
    return results
   