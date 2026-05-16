extract_seller_claims_prompt = """
You are an expert at analyzing product descriptions for fashion items (shoes, boxers, clothes, wristbands, etc.).

Extract all factual claims from this product description: "{description}".  
A claim is any statement describing a product feature, quality, or benefit.  

For each claim, identify the **most relevant aspect** from the following categories:
- sizing
- quality
- design
- item_accuracy
- delivery
- color_options
- comfort

Return **only** a JSON list. Each item in the list must have:
    - "claim": the claim text
    - "aspect": the mapped aspect from the categories above

Do not include any explanations, extra text, or items that are not claims.
"""