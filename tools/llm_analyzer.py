from openai import OpenAI

client = OpenAI()


def analyze_access_control(contract_code, optimzation):
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

    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
