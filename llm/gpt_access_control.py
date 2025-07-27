from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_access_control(source_code: str) -> str:
    prompt = f"""
    Analyze the following Solidity code for access control vulnerabilities.
    Focus on: missing onlyOwner, unrestricted sensitive functions, public mint/burn logic.

    Respond with a short bullet-point list of issues.

    Code:
    {source_code}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
