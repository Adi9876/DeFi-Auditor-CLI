def classify_severity(vulnerability_description: str) -> str:
    low_keywords = ["unused", "optimize", "gas", "external visibility"]
    high_keywords = ["reentrancy", "access control", "integer overflow", "flash loan", "oracle manipulation"]

    text = vulnerability_description.lower()
    if any(word in text for word in high_keywords):
        return "High"
    elif any(word in text for word in low_keywords):
        return "Low"
    return "Medium"
