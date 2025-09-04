#!/usr/bin/env python3
"""
Hybrid User Manager
Manages users with database primary and JSON fallback
"""

import json
import os
import hashlib
from typing import Optional, Dict, Any
from database_manager import (
    is_database_available, save_user_to_db, get_user_from_db, 
    get_user_by_email_from_db
)
from sync_manager import check_and_sync

class HybridUserManager:
    """Manages users with database primary and JSON fallback"""
    
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Ensure users.json exists"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users_from_json(self) -> Dict[str, Any]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users_to_json(self, users: Dict[str, Any]):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def save_user(self, username: str, email: str, password: str) -> bool:
        """Save user with database primary, JSON fallback"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check and sync before attempting database operations
        check_and_sync()
        
        # Try database first
        if is_database_available():
            success = save_user_to_db(username, email, password_hash)
            if success:
                print(f"✅ User '{username}' saved to database")
                return True
            else:
                print(f"⚠️ Database save failed for '{username}', falling back to JSON")
        
        # Fallback to JSON
        users = self._load_users_from_json()
        users[username] = {
            "username": username,
            "email": email,
            "password": password_hash
        }
        self._save_users_to_json(users)
        print(f"✅ User '{username}' saved to JSON file")
        
        # Try to sync immediately if database becomes available
        check_and_sync()
        
        return True
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user with database primary, JSON fallback"""
        # Try database first
        if is_database_available():
            user = get_user_from_db(username)
            if user:
                return {
                    "username": user["username"],
                    "email": user["email"],
                    "password": user["password_hash"]
                }
        
        # Fallback to JSON
        users = self._load_users_from_json()
        return users.get(username)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email with database primary, JSON fallback"""
        # Try database first
        if is_database_available():
            user = get_user_by_email_from_db(email)
            if user:
                return {
                    "username": user["username"],
                    "email": user["email"],
                    "password": user["password_hash"]
                }
        
        # Fallback to JSON
        users = self._load_users_from_json()
        for user_data in users.values():
            if user_data.get("email") == email:
                return user_data
        return None
    
    def get_user_case_insensitive(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by case-insensitive username lookup"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            # Use LOWER() function for case-insensitive comparison
            result = execute_database_query(
                "SELECT username, email, password_hash FROM users WHERE LOWER(username) = LOWER(%s)",
                (username,), fetch=True
            )
            if result:
                user = result[0]
                return {
                    "username": user["username"],
                    "email": user["email"],
                    "password": user["password_hash"]
                }
        
        # Fallback to JSON - case-insensitive lookup
        users = self._load_users_from_json()
        username_lower = username.lower()
        for stored_username, user_data in users.items():
            if stored_username.lower() == username_lower:
                return user_data
        return None
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return self.get_user(username) is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        return self.get_user_by_email(email) is not None
    
    def validate_user(self, username: str, password: str) -> bool:
        """Validate user credentials"""
        user = self.get_user(username)
        if not user:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user["password"] == password_hash
    
    def validate_user_case_insensitive(self, username: str, password: str) -> tuple[bool, Optional[str]]:
        """Validate user credentials with case-insensitive username lookup
        
        Returns:
            tuple: (is_valid, actual_username)
        """
        user = self.get_user_case_insensitive(username)
        if not user:
            return False, None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        is_valid = user["password"] == password_hash
        actual_username = user["username"] if is_valid else None
        return is_valid, actual_username
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users (for admin purposes)"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            result = execute_database_query("SELECT username, email, created_at FROM users", fetch=True)
            if result:
                users = {}
                for user in result:
                    users[user["username"]] = {
                        "username": user["username"],
                        "email": user["email"],
                        "created_at": str(user["created_at"])
                    }
                return users
        
        # Fallback to JSON
        return self._load_users_from_json()
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """Update user password"""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = "UPDATE users SET password_hash = %s WHERE username = %s"
            result = execute_database_query(query, (password_hash, username))
            if result:
                print(f"✅ Password updated for '{username}' in database")
                return True
        
        # Fallback to JSON
        users = self._load_users_from_json()
        if username in users:
            users[username]["password"] = password_hash
            self._save_users_to_json(users)
            print(f"✅ Password updated for '{username}' in JSON file")
            return True
        
        return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = "DELETE FROM users WHERE username = %s"
            result = execute_database_query(query, (username,))
            if result:
                print(f"✅ User '{username}' deleted from database")
                return True
        
        # Fallback to JSON
        users = self._load_users_from_json()
        if username in users:
            del users[username]
            self._save_users_to_json(users)
            print(f"✅ User '{username}' deleted from JSON file")
            return True
        
        return False

# Global instance
user_manager = HybridUserManager()

# Convenience functions
def save_user(username: str, email: str, password: str) -> bool:
    """Save user with hybrid system"""
    return user_manager.save_user(username, email, password)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user with hybrid system"""
    return user_manager.get_user(username)

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email with hybrid system"""
    return user_manager.get_user_by_email(email)

def user_exists(username: str) -> bool:
    """Check if user exists"""
    return user_manager.user_exists(username)

def email_exists(email: str) -> bool:
    """Check if email exists"""
    return user_manager.email_exists(email)

def validate_user(username: str, password: str) -> bool:
    """Validate user credentials"""
    return user_manager.validate_user(username, password)

def update_user_password(username: str, new_password: str) -> bool:
    """Update user password"""
    return user_manager.update_user_password(username, new_password)

def get_user_case_insensitive(username: str) -> Optional[Dict[str, Any]]:
    """Get user by case-insensitive username lookup"""
    return user_manager.get_user_case_insensitive(username)

def validate_user_credentials_case_insensitive(username: str, password: str) -> tuple[bool, Optional[str]]:
    """Validate user credentials with case-insensitive username lookup
    
    Returns:
        tuple: (is_valid, actual_username)
    """
    return user_manager.validate_user_case_insensitive(username, password)

if __name__ == "__main__":
    # Test the hybrid user manager
    print("Testing Hybrid User Manager...")
    
    # Test saving a user
    test_username = "testuser_db"
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    print(f"\n1. Saving user '{test_username}'...")
    success = save_user(test_username, test_email, test_password)
    print(f"Save result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test retrieving user
    print(f"\n2. Retrieving user '{test_username}'...")
    user = get_user(test_username)
    if user:
        print(f"✅ User found: {user['username']} ({user['email']})")
    else:
        print("❌ User not found")
    
    # Test validation
    print(f"\n3. Validating credentials...")
    valid = validate_user(test_username, test_password)
    print(f"Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    # Test email lookup
    print(f"\n4. Looking up by email...")
    user_by_email = get_user_by_email(test_email)
    if user_by_email:
        print(f"✅ User found by email: {user_by_email['username']}")
    else:
        print("❌ User not found by email")
    
    print("\n" + "="*50)
    print("Hybrid User Manager test complete!")
    print("="*50)
