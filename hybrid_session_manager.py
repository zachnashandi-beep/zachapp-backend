#!/usr/bin/env python3
"""
Hybrid Session Manager
Manages sessions with database primary and JSON fallback
"""

import json
import os
import time
import secrets
from typing import Optional, Dict, Any
from database_manager import (
    is_database_available, save_session_to_db, get_session_from_db, 
    delete_session_from_db, cleanup_expired_tokens_from_db
)
from sync_manager import check_and_sync

class HybridSessionManager:
    """Manages sessions with database primary and JSON fallback"""
    
    def __init__(self, sessions_file: str = "sessions.json"):
        self.sessions_file = sessions_file
        self._ensure_sessions_file()
    
    def _ensure_sessions_file(self):
        """Ensure sessions.json exists"""
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump({}, f)
    
    def _load_sessions_from_json(self) -> Dict[str, Any]:
        """Load sessions from JSON file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sessions_to_json(self, sessions: Dict[str, Any]):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def create_session(self, username: str, duration: int = 3600) -> str:
        """Create a new session"""
        token = secrets.token_hex(32)
        expiry = int(time.time()) + duration
        
        # Check and sync before attempting database operations
        check_and_sync()
        
        # Try database first
        if is_database_available():
            success = save_session_to_db(username, token, expiry)
            if success:
                print(f"✅ Session created for '{username}' in database")
                return token
            else:
                print(f"⚠️ Database session creation failed for '{username}', falling back to JSON")
        
        # Fallback to JSON
        sessions = self._load_sessions_from_json()
        sessions[username] = {
            "token": token,
            "expiry": expiry
        }
        self._save_sessions_to_json(sessions)
        print(f"✅ Session created for '{username}' in JSON file")
        
        # Try to sync immediately if database becomes available
        check_and_sync()
        
        return token
    
    def validate_session(self, username: str, token: str) -> bool:
        """Validate session and extend if valid (sliding session)"""
        current_time = int(time.time())
        
        # Try database first
        if is_database_available():
            session_data = get_session_from_db(username, token)
            if session_data:
                # Extend session (sliding session)
                new_expiry = current_time + 3600  # Extend by 1 hour
                save_session_to_db(username, token, new_expiry)
                print(f"✅ Session validated and extended for '{username}' in database")
                return True
            else:
                print(f"❌ Invalid or expired session for '{username}' in database")
                return False
        
        # Fallback to JSON
        sessions = self._load_sessions_from_json()
        if username in sessions:
            session_data = sessions[username]
            if (session_data["token"] == token and 
                session_data["expiry"] > current_time):
                
                # Extend session (sliding session)
                sessions[username]["expiry"] = current_time + 3600
                self._save_sessions_to_json(sessions)
                print(f"✅ Session validated and extended for '{username}' in JSON file")
                return True
            else:
                # Remove expired session
                del sessions[username]
                self._save_sessions_to_json(sessions)
                print(f"❌ Invalid or expired session for '{username}' in JSON file")
                return False
        
        print(f"❌ No session found for '{username}'")
        return False
    
    def end_session(self, username: str, token: str = None) -> bool:
        """End a session"""
        # Try database first
        if is_database_available():
            success = delete_session_from_db(username, token)
            if success:
                print(f"✅ Session ended for '{username}' in database")
                return True
            else:
                print(f"⚠️ Database session deletion failed for '{username}', falling back to JSON")
        
        # Fallback to JSON
        sessions = self._load_sessions_from_json()
        if username in sessions:
            if token is None or sessions[username]["token"] == token:
                del sessions[username]
                self._save_sessions_to_json(sessions)
                print(f"✅ Session ended for '{username}' in JSON file")
                return True
        
        return False
    
    def get_session_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = """
                SELECT token, UNIX_TIMESTAMP(expiry) as expiry_timestamp, created_at 
                FROM sessions 
                WHERE username = %s AND expiry > NOW()
            """
            result = execute_database_query(query, (username,), fetch=True)
            if result:
                session = result[0]
                return {
                    "token": session["token"],
                    "expiry": session["expiry_timestamp"],
                    "created_at": str(session["created_at"])
                }
        
        # Fallback to JSON
        sessions = self._load_sessions_from_json()
        if username in sessions:
            session_data = sessions[username]
            current_time = int(time.time())
            if session_data["expiry"] > current_time:
                return {
                    "token": session_data["token"],
                    "expiry": session_data["expiry"],
                    "created_at": "Unknown"
                }
        
        return None
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        # Try database first
        if is_database_available():
            cleanup_expired_tokens_from_db()
            print("✅ Expired sessions cleaned up in database")
            return
        
        # Fallback to JSON
        sessions = self._load_sessions_from_json()
        current_time = int(time.time())
        expired_users = []
        
        for username, session_data in sessions.items():
            if session_data["expiry"] <= current_time:
                expired_users.append(username)
        
        for username in expired_users:
            del sessions[username]
        
        if expired_users:
            self._save_sessions_to_json(sessions)
            print(f"✅ Cleaned up {len(expired_users)} expired sessions in JSON file")
        else:
            print("ℹ️ No expired sessions found in JSON file")

# Global instance
session_manager = HybridSessionManager()

# Convenience functions
def create_session(username: str, duration: int = 3600) -> str:
    """Create a new session"""
    return session_manager.create_session(username, duration)

def validate_session(username: str, token: str) -> bool:
    """Validate session"""
    return session_manager.validate_session(username, token)

def end_session(username: str, token: str = None) -> bool:
    """End a session"""
    return session_manager.end_session(username, token)

def get_session_info(username: str) -> Optional[Dict[str, Any]]:
    """Get session information"""
    return session_manager.get_session_info(username)

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    session_manager.cleanup_expired_sessions()

# Remember Me functionality
def save_remember_me(username: str, token: str):
    """Save remember me data"""
    remember_data = {
        "username": username,
        "token": token,
        "timestamp": int(time.time())
    }
    
    try:
        with open("remember_me.json", 'w') as f:
            json.dump(remember_data, f, indent=2)
        print(f"✅ Remember me data saved for '{username}'")
    except Exception as e:
        print(f"❌ Failed to save remember me data: {e}")

def load_remember_me() -> Optional[Dict[str, Any]]:
    """Load remember me data"""
    try:
        with open("remember_me.json", 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def clear_remember_me():
    """Clear remember me data"""
    try:
        if os.path.exists("remember_me.json"):
            os.remove("remember_me.json")
        print("✅ Remember me data cleared")
    except Exception as e:
        print(f"❌ Failed to clear remember me data: {e}")

def auto_login_from_remember() -> Optional[tuple]:
    """Auto-login from remember me data"""
    remember_data = load_remember_me()
    if not remember_data:
        return None
    
    username = remember_data.get("username")
    token = remember_data.get("token")
    
    if not username or not token:
        return None
    
    # Validate the remembered session
    if validate_session(username, token):
        print(f"✅ Auto-login successful for '{username}'")
        return (username, token)
    else:
        # Clear invalid remember me data
        clear_remember_me()
        print(f"❌ Auto-login failed for '{username}', remember me data cleared")
        return None

if __name__ == "__main__":
    # Test the hybrid session manager
    print("Testing Hybrid Session Manager...")
    
    test_username = "testuser_session"
    
    print(f"\n1. Creating session for '{test_username}'...")
    token = create_session(test_username, 3600)
    print(f"Session token: {token[:20]}...")
    
    print(f"\n2. Validating session...")
    valid = validate_session(test_username, token)
    print(f"Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    print(f"\n3. Getting session info...")
    session_info = get_session_info(test_username)
    if session_info:
        print(f"✅ Session info: expires at {time.ctime(session_info['expiry'])}")
    else:
        print("❌ No session info found")
    
    print(f"\n4. Testing remember me...")
    save_remember_me(test_username, token)
    auto_login = auto_login_from_remember()
    if auto_login:
        print(f"✅ Auto-login successful: {auto_login[0]}")
    else:
        print("❌ Auto-login failed")
    
    print(f"\n5. Ending session...")
    success = end_session(test_username, token)
    print(f"End session result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n" + "="*50)
    print("Hybrid Session Manager test complete!")
    print("="*50)
