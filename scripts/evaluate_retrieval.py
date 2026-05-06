from sqlalchemy import text
from database.connection import SessionLocal
from engine.retrieval import Retriever


# Test cases: (query, expected_case_titles_or_gr_nos)
TEST_CASES = [
    ("G.R. No. 242353", ["242353"]),  # Exact citation
    ("defamation", ["libel", "slander", "defamation"]),  # Topic search
    ("estafa", ["estafa", "fraud"]),  # Crime search
    ("labor rights", ["labor", "employee", "employer"]),  # Concept search
    ("habeas corpus", ["habeas", "detention"]),  # Procedure search
]


def evaluate():
    db = SessionLocal()
    retriever = Retriever(db)
    
    print("Evaluating retrieval quality...\n")
    
    total_tests = 0
    total_passed = 0
    
    for query, expected_keywords in TEST_CASES:
        total_tests += 1
        results = retriever.hybrid_search(query)
        
        print(f"Query: {query}")
        print(f"Results found: {len(results)}")
        
        # Check if any result contains expected keywords
        found_match = False
        for result in results[:5]:  # Check top 5
            case_text = f"{result[2]} {result[4]}".lower()  # title + clean_text
            
            if any(keyword.lower() in case_text for keyword in expected_keywords):
                found_match = True
                print(f"  Match: {result[2][:60]}...")
                break
        
        if found_match:
            total_passed += 1
            print("  Status: PASS")
        else:
            print("  Status: FAIL")
        
        print()
    
    # Print summary
    print(f"\nResults: {total_passed}/{total_tests} passed")
    print(f"Success rate: {100 * total_passed / total_tests:.1f}%")
    
    db.close()


if __name__ == "__main__":
    evaluate()