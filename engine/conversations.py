from datetime import datetime, timedelta
from uuid import uuid4

SESSIONS = {}
SESSION_TIMEOUT = timedelta(hours=1)


class ConversationSession:
    def __init__(self):
        self.session_id = str(uuid4())
        self.history = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def is_expired(self):
        return datetime.now() - self.last_activity > SESSION_TIMEOUT
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
    
    def get_context(self):
        """Return last 10 messages for LLM context"""
        return self.history[-10:] if len(self.history) > 0 else []


def get_or_create_session(session_id: str = None):
    """Get existing session or create new one"""
    if session_id and session_id in SESSIONS:
        session = SESSIONS[session_id]
        if not session.is_expired():
            return session
        else:
            del SESSIONS[session_id]
    
    session = ConversationSession()
    SESSIONS[session.session_id] = session
    return session


def cleanup_expired_sessions():
    """Remove expired sessions to free memory"""
    expired = [sid for sid, s in SESSIONS.items() if s.is_expired()]
    for sid in expired:
        del SESSIONS[sid]
    return len(expired)