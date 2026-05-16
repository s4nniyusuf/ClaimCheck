grammar_fix_prompt = """
You are an expert at editing English text.  
Here is a product description: "{description}"

Your task:
You are an expert editor. Here is a product description: "{description}"

Your task:
- Fix grammar, punctuation, capitalization, and run-on sentences.  
- Split long or confusing sentences into clear, readable sentences.  
- **Do not add or invent any new claims or features.**
- **If sentences are repeated, keep only the first instance**.  
- Keep all factual claims exactly as they appear.  
- Remove unnecessary filler words and repeated phrases.  
- Return the output as plain text only, ready to be fed into a claim-extraction model.

Example input: "This shoes fit perfectly it is very comfortable mens favorite"  
Example output: "These shoes fit perfectly. It is very comfortable. Mens favorite."

Now fix the following description:
"{description}"
"""