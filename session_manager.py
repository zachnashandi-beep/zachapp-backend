import os
import json
import time
import secrets
from typing import Dict, Optional, Tuple

class SessionManager:
    """Manages user sessions with sliding expiration"""
    
    def __init__(self, sessions_file: str = "sessions.json", remember_file: str = "remember.json"):
        self.sessions_file = sessions_file
        self.remember_file = remember_file
        self.default_duration = 3600  # 1 hour in seconds
    
    def _load_sessions(self) -> Dict:
        """Load sessions from JSON file"""
        try:
            if not os.path.exists(self.sessions_file):
                return {}
            with open(self.sessions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load sessions: {e}")
            return {}
    
    def _save_sessions(self, sessions: Dict) -> bool:
        """Save sessions to JSON file"""
        try:
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save sessions: {e}")
            return False
    
    def _load_remember_data(self) -> Dict:
        """Load remember me data"""
        try:
            if not os.path.exists(self.remember_file):
                return {}
            with open(self.remember_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load remember data: {e}")
            return {}
    
    def _save_remember_data(self, data: Dict) -> bool:
        """Save remember me data"""
        try:
            with open(self.remember_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save remember data: {e}")
            return False
    
    def create_session(self, username: str, duration: int = None) -> str:
        """
        Create a new session for the user
        
        Args:
            username: The username to create session for
            duration: Session duration in seconds (default: 1 hour)
            
        Returns:
            str: The generated session token
        """
        if duration is None:
            duration = self.default_duration
            
        # Generate secure token
        token = secrets.token_hex(32)
        expiry = int(time.time()) + duration
        
        # Load existing sessions
        sessions = self._load_sessions()
        
        # Create/update session
        sessions[username] = {
            "token": token,
            "expiry": expiry,
            "created": int(time.time())
        }
        
        # Save sessions
        if self._save_sessions(sessions):
            print(f"DEBUG: Created session for {username}, expires at {expiry}")
            return token
        else:
            raise Exception("Failed to save session")
    
    def validate_session(self, username: str, token: str, duration: int = None) -> bool:
        """
        Validate session and implement sliding expiration
        
        Args:
            username: The username to validate
            token: The session token to validate
            duration: How long to extend session if valid (default: 1 hour)
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        if duration is None:
            duration = self.default_duration
            
        sessions = self._load_sessions()
        current_time = int(time.time())
        
        # Check if user has a session
        if username not in sessions:
            print(f"DEBUG: No session found for {username}")
            return False
        
        session_data = sessions[username]
        
        # Check if token matches
        if session_data.get("token") != token:
            print(f"DEBUG: Token mismatch for {username}")
            return False
        
        # Check if session is expired
        if current_time > session_data.get("expiry", 0):
            print(f"DEBUG: Session expired for {username}")
            # Remove expired session
            del sessions[username]
            self._save_sessions(sessions)
            return False
        
        # Session is valid - implement sliding expiration
        new_expiry = current_time + duration
        sessions[username]["expiry"] = new_expiry
        
        if self._save_sessions(sessions):
            print(f"DEBUG: Session validated and extended for {username}, new expiry: {new_expiry}")
            return True
        else:
            print(f"DEBUG: Failed to extend session for {username}")
            return False
    
    def end_session(self, username: str) -> bool:
        """
        End a user's session
        
        Args:
            username: The username to end session for
            
        Returns:
            bool: True if session was ended successfully
        """
        sessions = self._load_sessions()
        
        if username in sessions:
            del sessions[username]
            if self._save_sessions(sessions):
                print(f"DEBUG: Ended session for {username}")
                return True
        
        return False
    
    def get_session_info(self, username: str) -> Optional[Dict]:
        """
        Get session information for a user
        
        Args:
            username: The username to get session info for
            
        Returns:
            Dict with session info or None if no session
        """
        sessions = self._load_sessions()
        return sessions.get(username)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions
        
        Returns:
            int: Number of sessions cleaned up
        """
        sessions = self._load_sessions()
        current_time = int(time.time())
        expired_users = []
        
        for username, session_data in sessions.items():
            if current_time > session_data.get("expiry", 0):
                expired_users.append(username)
        
        for username in expired_users:
            del sessions[username]
        
        if expired_users:
            self._save_sessions(sessions)
            print(f"DEBUG: Cleaned up {len(expired_users)} expired sessions")
        
        return len(expired_users)
    
    def save_remember_me(self, username: str, token: str) -> bool:
        """
        Save remember me data
        
        Args:
            username: The username to remember
            token: The session token to remember
            
        Returns:
            bool: True if saved successfully
        """
        data = {
            "username": username,
            "token": token,
            "timestamp": int(time.time())
        }
        return self._save_remember_data(data)
    
    def load_remember_me(self) -> Optional[Tuple[str, str]]:
        """
        Load remember me data
        
        Returns:
            Tuple of (username, token) or None if no remember data
        """
        data = self._load_remember_data()
        if data and "username" in data and "token" in data:
            return data["username"], data["token"]
        return None
    
    def clear_remember_me(self) -> bool:
        """
        Clear remember me data
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            if os.path.exists(self.remember_file):
                os.remove(self.remember_file)
            return True
        except Exception as e:
            print(f"Error: Failed to clear remember data: {e}")
            return False
    
    def auto_login_from_remember(self) -> Optional[str]:
        """
        Attempt auto-login from remember me data
        
        Returns:
            str: Username if auto-login successful, None otherwise
        """
        remember_data = self.load_remember_me()
        if not remember_data:
            return None
        
        username, token = remember_data
        
        # Validate the remembered session
        if self.validate_session(username, token):
            print(f"DEBUG: Auto-login successful for {username}")
            return username
        else:
            # Session is invalid, clear remember data
            self.clear_remember_me()
            print(f"DEBUG: Auto-login failed for {username}, cleared remember data")
            return None


# Global session manager instance
session_manager = SessionManager()


def create_session(username: str, duration: int = 3600) -> str:
    """Convenience function to create a session"""
    return session_manager.create_session(username, duration)


def validate_session(username: str, token: str, duration: int = 3600) -> bool:
    """Convenience function to validate a session"""
    return session_manager.validate_session(username, token, duration)


def end_session(username: str) -> bool:
    """Convenience function to end a session"""
    return session_manager.end_session(username)


def save_remember_me(username: str, token: str) -> bool:
    """Convenience function to save remember me data"""
    return session_manager.save_remember_me(username, token)


def load_remember_me() -> Optional[Tuple[str, str]]:
    """Convenience function to load remember me data"""
    return session_manager.load_remember_me()


def clear_remember_me() -> bool:
    """Convenience function to clear remember me data"""
    return session_manager.clear_remember_me()


def auto_login_from_remember() -> Optional[str]:
    """Convenience function to attempt auto-login"""
    return session_manager.auto_login_from_remember()


# Demo function to show usage
def demo_session_management():
    """Demonstrate session management functionality"""
    print("=== Session Management Demo ===")
    
    # Clean up any existing sessions
    session_manager.cleanup_expired_sessions()
    
    # Create a session
    username = "testuser"
    token = create_session(username, 3600)
    print(f"Created session for {username}: {token[:16]}...")
    
    # Validate session (should extend expiry)
    if validate_session(username, token):
        print(f"Session validated and extended for {username}")
    else:
        print(f"Session validation failed for {username}")
    
    # Get session info
    session_info = session_manager.get_session_info(username)
    if session_info:
        print(f"Session info: expires at {session_info['expiry']}")
    
    # Save remember me
    if save_remember_me(username, token):
        print(f"Remember me data saved for {username}")
    
    # Test auto-login
    auto_user = auto_login_from_remember()
    if auto_user:
        print(f"Auto-login successful for {auto_user}")
    else:
        print("Auto-login failed")
    
    # End session
    if end_session(username):
        print(f"Session ended for {username}")
    
    # Test validation after ending
    if not validate_session(username, token):
        print(f"Session correctly invalidated for {username}")
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    demo_session_management()
