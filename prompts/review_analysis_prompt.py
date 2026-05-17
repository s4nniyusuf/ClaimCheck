review_analysis_prompt = """
You are an expert at analyzing product reviews for any e-commerce category
(electronics, appliances, food, tools, furniture, health, fashion, software, etc.).

Your task is to extract aspects and their sentiment from a given review.

Use the following aspect categories only:
- physical_attributes  → size, weight, dimensions, fit, capacity, count
- build_quality        → materials, durability, construction, finish grade
- aesthetics           → visual design, color options, style, appearance, finish
- performance         → speed, power, accuracy, output, effectiveness, range
- usability            → ease of use, ergonomics, comfort, accessibility, controls
- compatibility        → supported devices, OS, standards, integrations, voltages
- contents             → what's included, bundled accessories, package variants
- safety_compliance   → certifications, safety ratings, regulatory standards, warnings
- sustainability       → eco-friendly materials, recyclability, ethical sourcing
- logistics            → shipping speed, delivery options, packaging, return policy

For each review:
- Identify which aspects are mentioned.
- For each aspect mentioned, classify the sentiment as: "positive", "negative", or "neutral".
- If an aspect is not mentioned, do not include it.

Example:

Review: "Fits perfectly, color was exactly as shown, but the material feels cheap and it arrived late."

Output:
{{"physical_attributes": "positive", "build_quality": "negative", "aesthetics": "positive", "logistics": "negative"}}

Now analyze the following review and return only the JSON:
"{review_text}"

Return ONLY the raw JSON object. No markdown fences, no backticks, no extra text.
"""