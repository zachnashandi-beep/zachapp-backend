#!/usr/bin/env python3
"""
Database Setup Script
Helps set up the database connection and password
"""

import os
import getpass
from database_manager import db_manager, is_database_available

def setup_database_password():
    """Setup database password"""
    print("=" * 70)
    print("DATABASE SETUP")
    print("=" * 70)
    
    print("Setting up AWS MySQL database connection...")
    print(f"Host: app.c9soige8csbp.eu-north-1.rds.amazonaws.com")
    print(f"Port: 3306")
    print(f"Database: myapp")
    print(f"Username: admin")
    
    # Check if password file exists
    if os.path.exists("db_password.txt"):
        print("\n✅ Password file found (db_password.txt)")
        choice = input("Do you want to update the password? (y/n): ").lower()
        if choice != 'y':
            print("Using existing password file.")
            return
    
    # Get password from user
    print("\nEnter your MySQL database password:")
    password = getpass.getpass("Password: ")
    
    if not password:
        print("❌ No password entered. Exiting.")
        return
    
    # Save password to file
    try:
        with open("db_password.txt", "w") as f:
            f.write(password)
        print("✅ Password saved to db_password.txt")
    except Exception as e:
        print(f"❌ Failed to save password: {e}")
        return
    
    # Test connection
    print("\nTesting database connection...")
    if is_database_available():
        print("✅ Database connection successful!")
        print("✅ Tables will be created automatically")
        print("✅ Your app is ready to use the database!")
    else:
        print("❌ Database connection failed!")
        print("   Check your password and network connection")
        print("   The app will use JSON fallback mode")

def install_requirements():
    """Install required packages"""
    print("\n" + "=" * 70)
    print("INSTALLING REQUIREMENTS")
    print("=" * 70)
    
    print("Installing required packages...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Requirements installed successfully!")
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        print("Please run manually: pip install -r requirements.txt")

def main():
    """Main setup function"""
    print("AWS MySQL Database Setup for Login Application")
    print("=" * 70)
    
    # Check if MySQL connector is available
    try:
        import mysql.connector
        print("✅ MySQL connector is available")
    except ImportError:
        print("❌ MySQL connector not found")
        print("Installing requirements...")
        install_requirements()
    
    # Setup database password
    setup_database_password()
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE")
    print("=" * 70)
    print("Next steps:")
    print("1. Run: python database_connection_test.py")
    print("2. If successful, your app will use the database")
    print("3. If failed, your app will use JSON fallback")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    main()
