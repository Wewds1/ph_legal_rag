def is_legal_question(query: str) -> bool:
    """Check if query is about Philippine law"""
    legal_keywords = [
        "law", "court", "case", "gr no", "g.r.", "supreme",
        "legal", "judge", "justice", "criminal", "civil",
        "crime", "contract", "defamation", "estafa", "murder",
        "theft", "rights", "constitution", "republic act",
        "statute", "jurisdiction", "liable", "accused",
        "plaintiff", "defendant", "petition", "appeal",
        "habeas corpus", "barangay", "labor", "employment",
        "fraud", "libel", "slander", "contract", "marriage",
        "inheritance", "property", "loan", "bail"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in legal_keywords)


def should_reject_query(query: str) -> bool:
    """Reject clearly off-topic queries"""
    reject_keywords = [
        "code", "programming", "python", "javascript",
        "recipe", "cooking", "palindrome", "math problem",
        "homework", "essay", "write me", "generate code",
        "function", "algorithm", "how to cook",
        "poem", "story", "novel", "song lyrics"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in reject_keywords)


def is_acknowledgement(query: str) -> bool:
    q = query.lower().strip()
    phrases = [
        "thanks", "thank you", "ty", "got it", "i understand",
        "noted", "okay", "ok", "sige", "salamat", "copy", "understood"
    ]
    return any(p in q for p in phrases)