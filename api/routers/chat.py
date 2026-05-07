from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import SearchRequest
from database.connection import get_db
from engine.retrieval import Retriever
from engine.generation import Generator
from engine.conversation import get_or_create_session, cleanup_expired_sessions
from engine.validators import is_legal_question, should_reject_query


router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(
    request: SearchRequest,
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with conversation memory and legal scope enforcement.
    
    Args:
        request: SearchRequest with query
        session_id: Optional session ID for conversation history
        db: Database session
    
    Returns:
        Chat response with answer, precedents, disclaimer, and session_id
    """
    try:
        # Clean up expired sessions
        cleanup_expired_sessions()
        
        # Validate query is not empty
        if not request.query or not request.query.strip():
            return {
                "answer": "Please ask a question about Philippine law.",
                "precedents": [],
                "disclaimer": "research only, not legal advice fr.",
                "session_id": session_id,
                "error": "Empty query"
            }
        
        # Get or create session
        session = get_or_create_session(session_id)
        
        # Store user message in history
        session.add_message("user", request.query)
        
        # Reject obviously off-topic queries
        if should_reject_query(request.query):
            response_text = "That's outside my scope. I only help with Philippine legal questions fr."
            session.add_message("assistant", response_text)
            
            return {
                "answer": response_text,
                "precedents": [],
                "disclaimer": "research only, not legal advice fr.",
                "session_id": session.session_id,
                "conversation_history": session.history
            }
        
        # Warn if query doesn't seem legal-related
        if not is_legal_question(request.query):
            response_text = "Hmm, that doesn't seem to be about Philippine law. Try asking about court cases, laws, or legal concepts instead."
            session.add_message("assistant", response_text)
            
            return {
                "answer": response_text,
                "precedents": [],
                "disclaimer": "research only, not legal advice fr.",
                "session_id": session.session_id,
                "conversation_history": session.history
            }
        
        # Retrieve cases from database
        retriever = Retriever(db)
        cases_result = retriever.hybrid_search(request.query)
        
        # Convert SQLAlchemy rows to dictionaries
        cases = []
        if cases_result:
            for row in cases_result:
                case_dict = {
                    "id": str(row[0]),
                    "gr_no": row[1],
                    "title": row[2],
                    "source_url": row[3],
                    "clean_text": row[4],
                    "snippet": row[4][:300] + "..." if len(row[4]) > 300 else row[4]
                }
                cases.append(case_dict)
        
        # Generate response with conversation context
        generator = Generator()
        response = generator.answer_with_context(
            query=request.query,
            cases=cases,
            history=session.get_context()
        )
        
        # Store assistant response in history
        session.add_message("assistant", response["answer"])
        
        # Return complete response
        return {
            "answer": response["answer"],
            "precedents": response.get("precedents", []),
            "disclaimer": response.get("disclaimer", "research only, not legal advice fr."),
            "session_id": session.session_id,
            "conversation_history": session.history,
            "cases_retrieved": len(cases)
        }
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return {
            "answer": "Oops, something went wrong. Try again?",
            "precedents": [],
            "disclaimer": "research only, not legal advice fr.",
            "session_id": session_id,
            "error": str(e)
        }


@router.get("/chat/session/{session_id}")
def get_session(session_id: str):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session ID to retrieve
    
    Returns:
        Conversation history
    """
    from engine.conversation import SESSIONS
    
    if session_id not in SESSIONS:
        return {"error": "Session not found or expired", "session_id": session_id}
    
    session = SESSIONS[session_id]
    
    if session.is_expired():
        del SESSIONS[session_id]
        return {"error": "Session expired", "session_id": session_id}
    
    return {
        "session_id": session_id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "message_count": len(session.history),
        "history": session.history
    }


@router.delete("/chat/session/{session_id}")
def end_session(session_id: str):
    """
    End a conversation session.
    
    Args:
        session_id: Session ID to end
    
    Returns:
        Confirmation
    """
    from engine.conversation import SESSIONS
    
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return {"message": f"Session {session_id} ended", "session_id": session_id}
    
    return {"error": "Session not found", "session_id": session_id}