import re

with open('agents.py', 'r') as f:
    content = f.read()

# Replace import
content = content.replace(
    'import google.generativeai as genai',
    'from groq import Groq\nimport os'
)

# Replace GenerationConfig function
content = re.sub(
    r'def _generation_config.*?return genai\.types\.GenerationConfig\(.*?\)',
    'def _get_groq_client():\n    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))',
    content, flags=re.DOTALL
)

# Replace model init in __init__
content = content.replace(
    'self.model: genai.GenerativeModel',
    'self.model: str'
)

# Replace generate_content calls with Groq
content = re.sub(
    r'response = self\.model\.generate_content\(\s*prompt.*?_generation_config\(\)\s*\)',
    '''client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            timeout=30
        )''',
    content, flags=re.DOTALL
)

# Replace response.text with Groq response format
content = content.replace(
    'response.text',
    'response.choices[0].message.content'
)

with open('agents.py', 'w') as f:
    f.write(content)

print("Done!")
