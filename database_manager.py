#!/usr/bin/env python3
"""
Database Manager
Handles MySQL database connections with JSON fallback
"""

import json
import os
import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple
import logging

# Try to import MySQL connector
try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("Warning: mysql-connector-python not installed. Install with: pip install mysql-connector-python")

# Database configuration
DB_CONFIG = {
    'host': 'app.c9soige8csbp.eu-north-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': '',  # Will be set from environment or prompt
    'database': 'myapp',
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 10,
    'sql_mode': 'TRADITIONAL'
}

class DatabaseManager:
    """Manages database connections and operations with JSON fallback"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.fallback_to_json = False
        self.logger = self._setup_logger()
        
        # Try to get password from environment or prompt
        self._setup_password()
        
        # Test connection
        self._test_connection()
    
    def _setup_logger(self):
        """Setup logging for database operations"""
        logger = logging.getLogger('DatabaseManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_password(self):
        """Setup database password from environment or prompt"""
        # Try to get password from environment variable
        password = os.getenv('DB_PASSWORD')
        
        if not password:
            # Try to get from a secure file
            try:
                with open('db_password.txt', 'r') as f:
                    password = f.read().strip()
            except FileNotFoundError:
                pass
        
        if not password:
            # Prompt user for password
            import getpass
            password = getpass.getpass("Enter MySQL database password: ")
        
        DB_CONFIG['password'] = password
    
    def _test_connection(self):
        """Test database connection"""
        if not MYSQL_AVAILABLE:
            self.logger.warning("MySQL connector not available, using JSON fallback")
            self.fallback_to_json = True
            return
        
        try:
            self.logger.info("Testing database connection...")
            
            # First try to connect without specifying database
            config_without_db = DB_CONFIG.copy()
            config_without_db.pop('database', None)
            
            self.connection = mysql.connector.connect(**config_without_db)
            
            if self.connection.is_connected():
                self.logger.info("Successfully connected to MySQL server")
                
                # Create database if it doesn't exist
                self._create_database_if_not_exists()
                
                # Now connect to the specific database
                self.connection.close()
                self.connection = mysql.connector.connect(**DB_CONFIG)
                
                if self.connection.is_connected():
                    self.is_connected = True
                    self.logger.info("Successfully connected to MySQL database")
                    
                    # Create tables if they don't exist
                    self._create_tables_if_not_exist()
                else:
                    self.logger.error("Failed to connect to specific database")
                    self.fallback_to_json = True
                
            else:
                self.logger.error("Failed to connect to database")
                self.fallback_to_json = True
                
        except Error as e:
            self.logger.error(f"Database connection error: {e}")
            self.fallback_to_json = True
            self.connection = None
    
    def _create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            self.logger.info(f"Database '{DB_CONFIG['database']}' is ready")
        except Error as e:
            self.logger.error(f"Error creating database: {e}")
    
    def _create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    expiry TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_token (token),
                    INDEX idx_expiry (expiry)
                )
            """)
            
            # Verification tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    expiry TIMESTAMP NOT NULL,
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_token (token),
                    INDEX idx_expiry (expiry)
                )
            """)
            
            # Password reset tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reset_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    expiry TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_token (token),
                    INDEX idx_expiry (expiry)
                )
            """)
            
            self.logger.info("Database tables created/verified successfully")
            
            # Check and update schema for existing tables
            self._update_schema_if_needed()
            
        except Error as e:
            self.logger.error(f"Error creating tables: {e}")
    
    def _update_schema_if_needed(self):
        """Update schema for existing tables if needed"""
        try:
            cursor = self.connection.cursor()
            
            # Check if reset_tokens table has updated_at column
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'reset_tokens' 
                AND COLUMN_NAME = 'updated_at'
            """, (DB_CONFIG['database'],))
            
            if not cursor.fetchone():
                # Add updated_at column to reset_tokens table
                self.logger.info("Adding updated_at column to reset_tokens table...")
                cursor.execute("""
                    ALTER TABLE reset_tokens 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """)
                self.logger.info("✅ Added updated_at column to reset_tokens table")
            else:
                self.logger.info("✅ reset_tokens table already has updated_at column")
            
            cursor.close()
            
        except Error as e:
            self.logger.error(f"Error updating schema: {e}")
    
    def get_connection(self):
        """Get database connection"""
        if self.is_connected and self.connection and self.connection.is_connected():
            return self.connection
        else:
            # Try to reconnect
            self._test_connection()
            return self.connection if self.is_connected else None
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """Execute a database query"""
        if self.fallback_to_json:
            self.logger.warning("Database not available, using JSON fallback")
            return None
        
        connection = self.get_connection()
        if not connection:
            self.logger.error("No database connection available")
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid if cursor.lastrowid else True
                
        except Error as e:
            self.logger.error(f"Database query error: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def is_database_available(self) -> bool:
        """Check if database is available"""
        return self.is_connected and not self.fallback_to_json

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def is_database_available() -> bool:
    """Check if database is available"""
    return db_manager.is_database_available()

def get_database_connection():
    """Get database connection"""
    return db_manager.get_connection()

def execute_database_query(query: str, params: Tuple = None, fetch: bool = False):
    """Execute database query"""
    return db_manager.execute_query(query, params, fetch)

# User management functions
def save_user_to_db(username: str, email: str, password_hash: str) -> bool:
    """Save user to database"""
    if not is_database_available():
        return False
    
    query = """
        INSERT INTO users (username, email, password_hash) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        email = VALUES(email), 
        password_hash = VALUES(password_hash),
        updated_at = CURRENT_TIMESTAMP
    """
    
    result = execute_database_query(query, (username, email, password_hash))
    return result is not None

def get_user_from_db(username: str) -> Optional[Dict]:
    """Get user from database"""
    if not is_database_available():
        return None
    
    query = "SELECT * FROM users WHERE username = %s"
    result = execute_database_query(query, (username,), fetch=True)
    return result[0] if result else None

def get_user_by_email_from_db(email: str) -> Optional[Dict]:
    """Get user by email from database"""
    if not is_database_available():
        return None
    
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_database_query(query, (email,), fetch=True)
    return result[0] if result else None

# Session management functions
def save_session_to_db(username: str, token: str, expiry: int) -> bool:
    """Save session to database"""
    if not is_database_available():
        return False
    
    query = """
        INSERT INTO sessions (username, token, expiry) 
        VALUES (%s, %s, FROM_UNIXTIME(%s))
        ON DUPLICATE KEY UPDATE 
        expiry = FROM_UNIXTIME(%s),
        updated_at = CURRENT_TIMESTAMP
    """
    
    result = execute_database_query(query, (username, token, expiry, expiry))
    return result is not None

def get_session_from_db(username: str, token: str) -> Optional[Dict]:
    """Get session from database"""
    if not is_database_available():
        return None
    
    query = """
        SELECT *, UNIX_TIMESTAMP(expiry) as expiry_timestamp 
        FROM sessions 
        WHERE username = %s AND token = %s AND expiry > NOW()
    """
    result = execute_database_query(query, (username, token), fetch=True)
    return result[0] if result else None

def delete_session_from_db(username: str, token: str = None) -> bool:
    """Delete session from database"""
    if not is_database_available():
        return False
    
    if token:
        query = "DELETE FROM sessions WHERE username = %s AND token = %s"
        params = (username, token)
    else:
        query = "DELETE FROM sessions WHERE username = %s"
        params = (username,)
    
    result = execute_database_query(query, params)
    return result is not None

# Verification token functions
def save_verification_token_to_db(username: str, email: str, token: str, expiry: int) -> bool:
    """Save verification token to database"""
    if not is_database_available():
        return False
    
    query = """
        INSERT INTO verification_tokens (username, email, token, expiry) 
        VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
        ON DUPLICATE KEY UPDATE 
        token = VALUES(token),
        expiry = VALUES(expiry),
        verified = FALSE,
        updated_at = CURRENT_TIMESTAMP
    """
    
    result = execute_database_query(query, (username, email, token, expiry))
    return result is not None

def get_verification_token_from_db(token: str) -> Optional[Dict]:
    """Get verification token from database"""
    if not is_database_available():
        return None
    
    query = """
        SELECT *, UNIX_TIMESTAMP(expiry) as expiry_timestamp 
        FROM verification_tokens 
        WHERE token = %s AND expiry > NOW()
    """
    result = execute_database_query(query, (token,), fetch=True)
    return result[0] if result else None

def mark_verification_token_verified(token: str) -> bool:
    """Mark verification token as verified"""
    if not is_database_available():
        return False
    
    query = "UPDATE verification_tokens SET verified = TRUE WHERE token = %s"
    result = execute_database_query(query, (token,))
    return result is not None

def is_user_verified_in_db(username: str) -> bool:
    """Check if user is verified in database"""
    if not is_database_available():
        return False
    
    query = """
        SELECT verified FROM verification_tokens 
        WHERE username = %s AND verified = TRUE
    """
    result = execute_database_query(query, (username,), fetch=True)
    return bool(result)

# Password reset token functions
def save_reset_token_to_db(username: str, email: str, token: str, expiry: int) -> bool:
    """Save password reset token to database"""
    if not is_database_available():
        return False
    
    query = """
        INSERT INTO reset_tokens (username, email, token, expiry) 
        VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
        ON DUPLICATE KEY UPDATE 
        token = VALUES(token),
        expiry = VALUES(expiry),
        updated_at = CURRENT_TIMESTAMP
    """
    
    result = execute_database_query(query, (username, email, token, expiry))
    return result is not None

def get_reset_token_from_db(token: str) -> Optional[Dict]:
    """Get password reset token from database"""
    if not is_database_available():
        return None
    
    query = """
        SELECT *, UNIX_TIMESTAMP(expiry) as expiry_timestamp 
        FROM reset_tokens 
        WHERE token = %s AND expiry > NOW()
    """
    result = execute_database_query(query, (token,), fetch=True)
    return result[0] if result else None

def delete_reset_token_from_db(token: str) -> bool:
    """Delete password reset token from database"""
    if not is_database_available():
        return False
    
    query = "DELETE FROM reset_tokens WHERE token = %s"
    result = execute_database_query(query, (token,))
    return result is not None

# Cleanup functions
def cleanup_expired_tokens_from_db() -> int:
    """Clean up expired tokens from database"""
    if not is_database_available():
        return 0
    
    # Clean up expired sessions
    session_query = "DELETE FROM sessions WHERE expiry < NOW()"
    execute_database_query(session_query)
    
    # Clean up expired verification tokens
    verification_query = "DELETE FROM verification_tokens WHERE expiry < NOW()"
    execute_database_query(verification_query)
    
    # Clean up expired reset tokens
    reset_query = "DELETE FROM reset_tokens WHERE expiry < NOW()"
    execute_database_query(reset_query)
    
    return 1  # Return 1 to indicate cleanup was performed

if __name__ == "__main__":
    # Test the database connection
    print("Testing database connection...")
    
    if is_database_available():
        print("✅ Database connection successful!")
        
        # Test a simple query
        result = execute_database_query("SELECT 1 as test", fetch=True)
        if result:
            print("✅ Database query test successful!")
        
        # Show database info
        print(f"Connected to: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        
    else:
        print("❌ Database connection failed, using JSON fallback")
    
    # Close connection
    db_manager.close_connection()
