import os
import google.generativeai as genai
from dotenv import load_dotenv

def analyze_access_control(contract_code, optimzation):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ GOOGLE_API_KEY environment variable not set. LLM analysis skipped."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    prompt = f"""
    You are a smart contract security auditor.
    Review the following Solidity contract code.
    Identify potential missing access controls.
    Focus on functions that should be restricted (like admin, withdraw, mint).

    Return a short bullet list of your findings.

    Contract:
    {contract_code}

    Along with some basic optimization insights for extra context:
    {optimzation}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ LLM Analysis failed: {str(e)}"
