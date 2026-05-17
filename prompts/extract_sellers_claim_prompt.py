extract_seller_claims_prompt = """
You are an expert at analyzing product descriptions for any e-commerce category
(electronics, appliances, food, tools, furniture, health, fashion, software, etc.).

Extract all factual claims from this product description: "{description}".
A claim is any statement that describes a product feature, characteristic, or benefit.

For each claim, identify the most relevant aspect from the following categories:

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

Rules:
- Extract only objective, verifiable claims — skip vague marketing phrases like
  "best in class" or "amazing quality" unless they reference a specific attribute.
- If a claim spans multiple aspects, choose the single most specific one.
- Return ONLY a JSON array. No preamble, no explanation, no markdown fences.

Each item must have exactly two keys:
  - "claim": the claim text (concise, preserved from the description)
  - "aspect": one value from the aspect list above

Example output:
[
  {"claim": "Made from 304 stainless steel", "aspect": "build_quality"},
  {"claim": "Compatible with Alexa and Google Home", "aspect": "compatibility"},
  {"claim": "Ships within 24 hours", "aspect": "logistics"}
]
"""