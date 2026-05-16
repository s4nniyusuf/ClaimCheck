review_analysis_prompt = """
You are an expert at analyzing product reviews for fashion items (shoes, boxers, clothes, wristbands, etc.).

Your task is to extract **aspects** and their **sentiment** from a given review.

Use the following **aspect categories only**:
- sizing
- quality
- design
- item_accuracy
- delivery
- color_options
- comfort

For each review:
- Identify which aspects are mentioned.
- For each aspect mentioned, classify the sentiment as: "positive", "negative", or "neutral".
- If an aspect is not mentioned, do not include it.
- Return the result strictly as **JSON**, in the following format:

{{
  "sizing": "positive/negative/neutral",
  "quality": "positive/negative/neutral",
  "design": "positive/negative/neutral",
  "item_accuracy": "positive/negative/neutral",
  "delivery": "positive/negative/neutral",
  "color_options": "positive/negative/neutral",
  "comfort": "positive/negative/neutral"
}}

Example:

Review: "The shoes fit perfectly, the color was exactly as advertised, but the material feels cheap."

Output:
{{"sizing": "positive", "quality": "negative", "item_accuracy": "positive"}}

Now analyze the following review and return only the JSON:
"{review_text}"

Return ONLY the raw JSON object. Do not wrap it in markdown code fences or backticks. Do not add any newlines before or after the JSON.

"""