"""In-memory session store. No relational DB: this is a local, single-user
prototype, so a TTL cache living in process memory is enough and is much
faster than round-tripping to disk or a real database.
"""
import uuid

from cachetools import TTLCache

# 2 hour TTL, generous size since payloads are small (a few dozen respondents each)
_sessions: TTLCache = TTLCache(maxsize=200, ttl=2 * 60 * 60)


def create_session(data: dict) -> str:
    session_id = uuid.uuid4().hex
    _sessions[session_id] = data
    return session_id


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def update_session(session_id: str, **fields) -> dict:
    session = _sessions.get(session_id)
    if session is None:
        raise KeyError(session_id)
    session.update(fields)
    _sessions[session_id] = session
    return session
