#!/usr/bin/env python3
"""
Check Offline Status
Verify system is ready for offline testing
"""

import os
from database_manager import is_database_available

def check_offline_status():
    """Check if system is ready for offline testing"""
    print("🔍 CURRENT SYSTEM STATUS")
    print("=" * 50)
    
    # Database status
    db_available = is_database_available()
    print(f"Database Available: {'✅ Yes' if db_available else '❌ No (Offline)'}")
    print(f"JSON Fallback Active: {'✅ Yes' if not db_available else '⚠️ DB Online'}")
    print()
    
    # JSON files status
    print("📁 JSON Files Status:")
    json_files = ['users.json', 'sessions.json', 'verification.json', 'reset_tokens.json']
    all_files_exist = True
    
    for file in json_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  {file}: ✅ Exists ({size} bytes)")
        else:
            print(f"  {file}: ❌ Missing")
            all_files_exist = False
    
    print()
    
    # System readiness
    if not db_available and all_files_exist:
        print("🎯 System Ready for Offline Testing!")
        print("✅ All operations will use JSON fallback")
        print("✅ Sync system will queue data for later")
        print("✅ No database connection required")
    elif db_available:
        print("⚠️ Database is online - testing hybrid mode")
    else:
        print("❌ Some JSON files missing - may need initialization")
    
    print()
    print("📋 Ready to test:")
    print("  • Signup (creates users.json entries)")
    print("  • Login (reads from users.json)")
    print("  • Email verification (uses verification.json)")
    print("  • Password reset (uses reset_tokens.json)")
    print("  • Session management (uses sessions.json)")

if __name__ == "__main__":
    check_offline_status()
