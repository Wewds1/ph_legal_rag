def is_legal_question(query: str) -> bool:
    """Check if query is about Philippine law"""
    legal_keywords = [
        "law", "court", "case", "gr no", "supreme", "legal",
        "crime", "contract", "civil", "criminal", "constitution",
        "republic act", "statute", "statute", "jurisdiction",
        "defamation", "estafa", "murder", "theft", "rights"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in legal_keywords)


def should_reject_query(query: str) -> bool:
    """Reject clearly off-topic queries"""
    reject_keywords = [
        "code", "programming", "python", "javascript",
        "recipe", "cooking", "palindrome", "math problem",
        "homework", "essay"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in reject_keywords)