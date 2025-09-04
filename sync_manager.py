#!/usr/bin/env python3
"""
Sync Manager
Handles synchronization between JSON files and database
"""

import json
import os
import time
import logging
from typing import Dict, List, Any, Optional, Set
from database_manager import (
    is_database_available, execute_database_query, db_manager
)

class SyncManager:
    """Manages synchronization between JSON files and database"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.sync_tracking_file = "sync_tracking.json"
        self.sync_tracking = self._load_sync_tracking()
        self.last_db_status = False
        self.sync_in_progress = False
        
    def _setup_logger(self):
        """Setup logging for sync operations"""
        logger = logging.getLogger('SyncManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_sync_tracking(self) -> Dict[str, Any]:
        """Load sync tracking data"""
        try:
            if os.path.exists(self.sync_tracking_file):
                with open(self.sync_tracking_file, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return {
            "last_sync": 0,
            "synced_users": {},
            "synced_sessions": {},
            "synced_verification": {},
            "synced_reset_tokens": {},
            "failed_syncs": []
        }
    
    def _save_sync_tracking(self):
        """Save sync tracking data"""
        try:
            with open(self.sync_tracking_file, 'w') as f:
                json.dump(self.sync_tracking, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save sync tracking: {e}")
    
    def _mark_as_synced(self, data_type: str, key: str, timestamp: int = None):
        """Mark an entry as synced"""
        if timestamp is None:
            timestamp = int(time.time())
        
        if data_type not in self.sync_tracking:
            self.sync_tracking[data_type] = {}
        
        self.sync_tracking[data_type][key] = timestamp
        self._save_sync_tracking()
    
    def _is_synced(self, data_type: str, key: str) -> bool:
        """Check if an entry is already synced"""
        return key in self.sync_tracking.get(data_type, {})
    
    def _get_unsynced_entries(self, data_type: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get entries that haven't been synced yet"""
        synced_keys = set(self.sync_tracking.get(data_type, {}).keys())
        return {k: v for k, v in json_data.items() if k not in synced_keys}
    
    def check_and_sync(self) -> bool:
        """Check database availability and sync if needed"""
        current_db_status = is_database_available()
        
        # If database just became available, trigger sync
        if current_db_status and not self.last_db_status:
            self.logger.info("Database connection restored, starting sync...")
            return self.sync_all_data()
        
        # If database is available and we haven't synced recently, do a periodic sync
        elif current_db_status and self._should_periodic_sync():
            self.logger.info("Periodic sync triggered...")
            return self.sync_all_data()
        
        self.last_db_status = current_db_status
        return True
    
    def _should_periodic_sync(self) -> bool:
        """Check if we should do a periodic sync"""
        last_sync = self.sync_tracking.get("last_sync", 0)
        current_time = int(time.time())
        # Sync every 5 minutes if database is available
        return (current_time - last_sync) > 300
    
    def sync_all_data(self) -> bool:
        """Sync all JSON data to database"""
        if self.sync_in_progress:
            self.logger.warning("Sync already in progress, skipping...")
            return True
        
        if not is_database_available():
            self.logger.warning("Database not available, cannot sync")
            return False
        
        self.sync_in_progress = True
        success = True
        
        try:
            self.logger.info("Starting comprehensive data sync...")
            
            # Sync users
            if not self.sync_users():
                success = False
            
            # Sync sessions
            if not self.sync_sessions():
                success = False
            
            # Sync verification tokens
            if not self.sync_verification_tokens():
                success = False
            
            # Sync reset tokens
            if not self.sync_reset_tokens():
                success = False
            
            # Update last sync timestamp
            self.sync_tracking["last_sync"] = int(time.time())
            self._save_sync_tracking()
            
            if success:
                self.logger.info("✅ All data synchronized successfully")
            else:
                self.logger.warning("⚠️ Some data sync operations failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Sync failed with error: {e}")
            return False
        finally:
            self.sync_in_progress = False
    
    def sync_users(self) -> bool:
        """Sync users from JSON to database"""
        try:
            if not os.path.exists("users.json"):
                return True
            
            with open("users.json", 'r') as f:
                users = json.load(f)
            
            unsynced_users = self._get_unsynced_entries("synced_users", users)
            
            if not unsynced_users:
                self.logger.info("No unsynced users found")
                return True
            
            self.logger.info(f"Syncing {len(unsynced_users)} users to database...")
            
            for username, user_data in unsynced_users.items():
                try:
                    # Insert or update user in database
                    query = """
                        INSERT INTO users (username, email, password_hash) 
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        email = VALUES(email), 
                        password_hash = VALUES(password_hash),
                        updated_at = CURRENT_TIMESTAMP
                    """
                    
                    result = execute_database_query(
                        query, 
                        (user_data["username"], user_data["email"], user_data["password"])
                    )
                    
                    if result:
                        self._mark_as_synced("synced_users", username)
                        self.logger.info(f"✅ Synced user: {username}")
                    else:
                        self.logger.error(f"❌ Failed to sync user: {username}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error syncing user {username}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync users: {e}")
            return False
    
    def sync_sessions(self) -> bool:
        """Sync sessions from JSON to database"""
        try:
            if not os.path.exists("sessions.json"):
                return True
            
            with open("sessions.json", 'r') as f:
                sessions = json.load(f)
            
            unsynced_sessions = self._get_unsynced_entries("synced_sessions", sessions)
            
            if not unsynced_sessions:
                self.logger.info("No unsynced sessions found")
                return True
            
            self.logger.info(f"Syncing {len(unsynced_sessions)} sessions to database...")
            
            for username, session_data in unsynced_sessions.items():
                try:
                    # Check if session is still valid (not expired)
                    current_time = int(time.time())
                    if session_data["expiry"] <= current_time:
                        self.logger.info(f"⏭️ Skipping expired session for: {username}")
                        self._mark_as_synced("synced_sessions", username)
                        continue
                    
                    # Insert or update session in database
                    query = """
                        INSERT INTO sessions (username, token, expiry) 
                        VALUES (%s, %s, FROM_UNIXTIME(%s))
                        ON DUPLICATE KEY UPDATE 
                        expiry = FROM_UNIXTIME(%s),
                        updated_at = CURRENT_TIMESTAMP
                    """
                    
                    result = execute_database_query(
                        query, 
                        (username, session_data["token"], session_data["expiry"], session_data["expiry"])
                    )
                    
                    if result:
                        self._mark_as_synced("synced_sessions", username)
                        self.logger.info(f"✅ Synced session: {username}")
                    else:
                        self.logger.error(f"❌ Failed to sync session: {username}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error syncing session {username}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync sessions: {e}")
            return False
    
    def sync_verification_tokens(self) -> bool:
        """Sync verification tokens from JSON to database"""
        try:
            if not os.path.exists("verification.json"):
                return True
            
            with open("verification.json", 'r') as f:
                verification = json.load(f)
            
            unsynced_verification = self._get_unsynced_entries("synced_verification", verification)
            
            if not unsynced_verification:
                self.logger.info("No unsynced verification tokens found")
                return True
            
            self.logger.info(f"Syncing {len(unsynced_verification)} verification tokens to database...")
            
            for username, token_data in unsynced_verification.items():
                try:
                    # Check if token is still valid (not expired)
                    current_time = int(time.time())
                    if token_data["expiry"] <= current_time:
                        self.logger.info(f"⏭️ Skipping expired verification token for: {username}")
                        self._mark_as_synced("synced_verification", username)
                        continue
                    
                    # Insert or update verification token in database
                    query = """
                        INSERT INTO verification_tokens (username, email, token, expiry, verified) 
                        VALUES (%s, %s, %s, FROM_UNIXTIME(%s), %s)
                        ON DUPLICATE KEY UPDATE 
                        token = VALUES(token),
                        expiry = VALUES(expiry),
                        verified = VALUES(verified),
                        updated_at = CURRENT_TIMESTAMP
                    """
                    
                    result = execute_database_query(
                        query, 
                        (username, token_data["email"], token_data["token"], 
                         token_data["expiry"], token_data["verified"])
                    )
                    
                    if result:
                        self._mark_as_synced("synced_verification", username)
                        self.logger.info(f"✅ Synced verification token: {username}")
                    else:
                        self.logger.error(f"❌ Failed to sync verification token: {username}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error syncing verification token {username}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync verification tokens: {e}")
            return False
    
    def sync_reset_tokens(self) -> bool:
        """Sync reset tokens from JSON to database"""
        try:
            if not os.path.exists("reset_tokens.json"):
                return True
            
            with open("reset_tokens.json", 'r') as f:
                reset_tokens = json.load(f)
            
            unsynced_reset_tokens = self._get_unsynced_entries("synced_reset_tokens", reset_tokens)
            
            if not unsynced_reset_tokens:
                self.logger.info("No unsynced reset tokens found")
                return True
            
            self.logger.info(f"Syncing {len(unsynced_reset_tokens)} reset tokens to database...")
            
            for token, token_data in unsynced_reset_tokens.items():
                try:
                    # Check if token is still valid (not expired)
                    current_time = int(time.time())
                    if token_data["expiry"] <= current_time:
                        self.logger.info(f"⏭️ Skipping expired reset token: {token[:20]}...")
                        self._mark_as_synced("synced_reset_tokens", token)
                        continue
                    
                    # Insert or update reset token in database
                    query = """
                        INSERT INTO reset_tokens (username, email, token, expiry) 
                        VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
                        ON DUPLICATE KEY UPDATE 
                        token = VALUES(token),
                        expiry = VALUES(expiry)
                    """
                    
                    result = execute_database_query(
                        query, 
                        (token_data["username"], token_data["email"], token, token_data["expiry"])
                    )
                    
                    if result:
                        self._mark_as_synced("synced_reset_tokens", token)
                        self.logger.info(f"✅ Synced reset token: {token[:20]}...")
                    else:
                        self.logger.error(f"❌ Failed to sync reset token: {token[:20]}...")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error syncing reset token {token[:20]}...: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync reset tokens: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "database_available": is_database_available(),
            "last_sync": self.sync_tracking.get("last_sync", 0),
            "sync_in_progress": self.sync_in_progress,
            "synced_counts": {
                "users": len(self.sync_tracking.get("synced_users", {})),
                "sessions": len(self.sync_tracking.get("synced_sessions", {})),
                "verification": len(self.sync_tracking.get("synced_verification", {})),
                "reset_tokens": len(self.sync_tracking.get("synced_reset_tokens", {}))
            },
            "failed_syncs": len(self.sync_tracking.get("failed_syncs", []))
        }
    
    def clear_sync_tracking(self):
        """Clear sync tracking (useful for testing)"""
        self.sync_tracking = {
            "last_sync": 0,
            "synced_users": {},
            "synced_sessions": {},
            "synced_verification": {},
            "synced_reset_tokens": {},
            "failed_syncs": []
        }
        self._save_sync_tracking()
        self.logger.info("Sync tracking cleared")

# Global sync manager instance
sync_manager = SyncManager()

# Convenience functions
def check_and_sync():
    """Check database availability and sync if needed"""
    return sync_manager.check_and_sync()

def sync_all_data():
    """Sync all JSON data to database"""
    return sync_manager.sync_all_data()

def get_sync_status():
    """Get current sync status"""
    return sync_manager.get_sync_status()

def clear_sync_tracking():
    """Clear sync tracking"""
    sync_manager.clear_sync_tracking()

if __name__ == "__main__":
    # Test the sync manager
    print("Testing Sync Manager...")
    
    # Check sync status
    status = get_sync_status()
    print(f"Database available: {status['database_available']}")
    print(f"Last sync: {time.ctime(status['last_sync']) if status['last_sync'] else 'Never'}")
    print(f"Sync in progress: {status['sync_in_progress']}")
    print(f"Synced counts: {status['synced_counts']}")
    
    # Try to sync
    if status['database_available']:
        print("\nAttempting sync...")
        success = sync_all_data()
        print(f"Sync result: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("\nDatabase not available, cannot sync")
