#!/usr/bin/env python3
"""
Forgot Password System Demo
Comprehensive demonstration of the password reset functionality
"""

import sys
import os
import json
import time
from PyQt6 import QtWidgets, QtCore, QtGui
from password_reset_manager import (
    generate_reset_token, validate_reset_token, reset_password, 
    send_reset_email_simulation, cleanup_expired_tokens
)
from forgot_password_dialog import show_forgot_password_dialog
from reset_password_dialog import show_reset_password_dialog

class ForgotPasswordDemoWindow(QtWidgets.QMainWindow):
    """Demo window for forgot password system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forgot Password System Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add title
        title = QtWidgets.QLabel("Forgot Password System Demo")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        """)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        description = QtWidgets.QLabel("""
        This demo showcases the complete forgot password workflow:
        <ol>
            <li><b>Request Reset:</b> User enters username/email to request password reset</li>
            <li><b>Token Generation:</b> System generates secure token and stores it</li>
            <li><b>Email Simulation:</b> Reset link is sent to user's email</li>
            <li><b>Password Reset:</b> User clicks link and enters new password</li>
            <li><b>Login:</b> User can now login with new password</li>
        </ol>
        """)
        description.setStyleSheet("""
            font-size: 14px;
            color: #34495e;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin: 10px;
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add demo buttons
        button_layout = QtWidgets.QGridLayout()
        
        # Test user creation
        self.create_user_btn = QtWidgets.QPushButton("Create Test User")
        self.create_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.create_user_btn.clicked.connect(self.create_test_user)
        button_layout.addWidget(self.create_user_btn, 0, 0)
        
        # Forgot password dialog
        self.forgot_btn = QtWidgets.QPushButton("Open Forgot Password Dialog")
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.forgot_btn.clicked.connect(self.open_forgot_password_dialog)
        button_layout.addWidget(self.forgot_btn, 0, 1)
        
        # Reset password dialog
        self.reset_btn = QtWidgets.QPushButton("Open Reset Password Dialog")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.reset_btn.clicked.connect(self.open_reset_password_dialog)
        button_layout.addWidget(self.reset_btn, 0, 2)
        
        # Token management
        self.cleanup_btn = QtWidgets.QPushButton("Cleanup Expired Tokens")
        self.cleanup_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.cleanup_btn.clicked.connect(self.cleanup_tokens)
        button_layout.addWidget(self.cleanup_btn, 1, 0)
        
        # Test token generation
        self.test_token_btn = QtWidgets.QPushButton("Test Token Generation")
        self.test_token_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.test_token_btn.clicked.connect(self.test_token_generation)
        button_layout.addWidget(self.test_token_btn, 1, 1)
        
        # View tokens
        self.view_tokens_btn = QtWidgets.QPushButton("View Active Tokens")
        self.view_tokens_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        self.view_tokens_btn.clicked.connect(self.view_active_tokens)
        button_layout.addWidget(self.view_tokens_btn, 1, 2)
        
        layout.addLayout(button_layout)
        
        # Add status area
        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        self.status_text.setMaximumHeight(200)
        layout.addWidget(self.status_text)
        
        # Add some spacing
        layout.addStretch()
        
        # Initialize status
        self.log_status("Forgot Password System Demo initialized")
        self.log_status("Click 'Create Test User' to start the demo")
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        self.status_text.ensureCursorVisible()
    
    def create_test_user(self):
        """Create a test user for demo purposes"""
        try:
            # Load existing users
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", 'r') as f:
                    users = json.load(f)
            
            # Create test user
            import hashlib
            test_user = {
                "username": "testuser",
                "email": "test@example.com",
                "password": hashlib.sha256("oldpassword".encode()).hexdigest()
            }
            
            # Add to users (overwrite if exists)
            users["testuser"] = test_user
            
            # Save users
            with open("users.json", 'w') as f:
                json.dump(users, f, indent=2)
            
            self.log_status("✅ Test user created: testuser / test@example.com")
            self.log_status("   Password: oldpassword")
            self.log_status("   You can now test the forgot password flow")
            
        except Exception as e:
            self.log_status(f"❌ Error creating test user: {e}")
    
    def open_forgot_password_dialog(self):
        """Open the forgot password dialog"""
        try:
            self.log_status("Opening Forgot Password Dialog...")
            result = show_forgot_password_dialog(self)
            
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                self.log_status("✅ Forgot password dialog completed successfully")
            else:
                self.log_status("ℹ️ Forgot password dialog cancelled")
                
        except Exception as e:
            self.log_status(f"❌ Error opening forgot password dialog: {e}")
    
    def open_reset_password_dialog(self):
        """Open the reset password dialog"""
        try:
            self.log_status("Opening Reset Password Dialog...")
            result = show_reset_password_dialog(None, self)
            
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                self.log_status("✅ Reset password dialog completed successfully")
            else:
                self.log_status("ℹ️ Reset password dialog cancelled")
                
        except Exception as e:
            self.log_status(f"❌ Error opening reset password dialog: {e}")
    
    def cleanup_tokens(self):
        """Clean up expired tokens"""
        try:
            self.log_status("Cleaning up expired tokens...")
            cleanup_expired_tokens()
            self.log_status("✅ Token cleanup completed")
        except Exception as e:
            self.log_status(f"❌ Error during token cleanup: {e}")
    
    def test_token_generation(self):
        """Test token generation for test user"""
        try:
            self.log_status("Testing token generation for 'testuser'...")
            token = generate_reset_token("testuser")
            
            if token:
                self.log_status(f"✅ Token generated successfully: {token[:20]}...")
                
                # Validate token
                token_data = validate_reset_token(token)
                if token_data:
                    self.log_status(f"✅ Token validation successful")
                    self.log_status(f"   Username: {token_data['username']}")
                    self.log_status(f"   Email: {token_data['email']}")
                    self.log_status(f"   Expires: {time.ctime(token_data['expiry'])}")
                else:
                    self.log_status("❌ Token validation failed")
            else:
                self.log_status("❌ Token generation failed - user not found")
                
        except Exception as e:
            self.log_status(f"❌ Error during token generation test: {e}")
    
    def view_active_tokens(self):
        """View active reset tokens"""
        try:
            self.log_status("Viewing active reset tokens...")
            
            if not os.path.exists("reset_tokens.json"):
                self.log_status("ℹ️ No reset tokens file found")
                return
            
            with open("reset_tokens.json", 'r') as f:
                tokens = json.load(f)
            
            if not tokens:
                self.log_status("ℹ️ No active reset tokens found")
                return
            
            self.log_status(f"📋 Found {len(tokens)} active token(s):")
            current_time = int(time.time())
            
            for token, data in tokens.items():
                expiry_time = data['expiry']
                is_expired = current_time > expiry_time
                status = "❌ EXPIRED" if is_expired else "✅ ACTIVE"
                
                self.log_status(f"   Token: {token[:20]}...")
                self.log_status(f"   User: {data['username']}")
                self.log_status(f"   Email: {data['email']}")
                self.log_status(f"   Expires: {time.ctime(expiry_time)}")
                self.log_status(f"   Status: {status}")
                self.log_status("   " + "-" * 40)
                
        except Exception as e:
            self.log_status(f"❌ Error viewing tokens: {e}")

def demo_forgot_password_system():
    """Console demo of the forgot password system"""
    print("=" * 70)
    print("FORGOT PASSWORD SYSTEM DEMO")
    print("=" * 70)
    
    print("\n1. System Overview:")
    print("   ✅ Secure token generation using secrets.token_hex(32)")
    print("   ✅ Token expiry management (default: 1 hour)")
    print("   ✅ Email simulation for reset links")
    print("   ✅ Password strength validation")
    print("   ✅ Token cleanup and management")
    
    print("\n2. Workflow:")
    print("   Step 1: User clicks 'Forgot Password' on login page")
    print("   Step 2: User enters username or email")
    print("   Step 3: System generates secure token")
    print("   Step 4: Reset link sent to user's email")
    print("   Step 5: User clicks link and enters new password")
    print("   Step 6: Password updated and token deleted")
    
    print("\n3. Security Features:")
    print("   🔒 64-character secure tokens (secrets.token_hex(32))")
    print("   🔒 Token expiry (1 hour default)")
    print("   🔒 Automatic token cleanup")
    print("   🔒 Password strength validation")
    print("   🔒 SHA256 password hashing")
    
    print("\n4. File Structure:")
    print("   📁 reset_tokens.json - Stores active reset tokens")
    print("   📁 users.json - User database")
    print("   📁 password_reset_manager.py - Core reset logic")
    print("   📁 forgot_password_dialog.py - Request dialog")
    print("   📁 reset_password_dialog.py - Reset dialog")
    
    print("\n5. Integration:")
    print("   ✅ Integrated with existing login system")
    print("   ✅ Works with session management")
    print("   ✅ Compatible with email verification")
    print("   ✅ Modern, user-friendly dialogs")
    
    print("\n" + "=" * 70)
    print("FORGOT PASSWORD SYSTEM DEMO COMPLETE")
    print("=" * 70)

def test_password_reset_workflow():
    """Test the complete password reset workflow"""
    print("\n" + "=" * 70)
    print("PASSWORD RESET WORKFLOW TEST")
    print("=" * 70)
    
    # Test user data
    test_username = "testuser"
    test_email = "test@example.com"
    old_password = "oldpassword"
    new_password = "newpassword123"
    
    print(f"\nTesting with user: {test_username}")
    print(f"Email: {test_email}")
    print(f"Old password: {old_password}")
    print(f"New password: {new_password}")
    
    try:
        # Step 1: Generate reset token
        print("\nStep 1: Generating reset token...")
        token = generate_reset_token(test_username)
        
        if not token:
            print("❌ Token generation failed - user not found")
            print("   Make sure to create test user first")
            return
        
        print(f"✅ Token generated: {token[:20]}...")
        
        # Step 2: Validate token
        print("\nStep 2: Validating token...")
        token_data = validate_reset_token(token)
        
        if not token_data:
            print("❌ Token validation failed")
            return
        
        print(f"✅ Token valid for: {token_data['username']}")
        print(f"   Email: {token_data['email']}")
        print(f"   Expires: {time.ctime(token_data['expiry'])}")
        
        # Step 3: Reset password
        print("\nStep 3: Resetting password...")
        success = reset_password(token, new_password)
        
        if success:
            print("✅ Password reset successful")
        else:
            print("❌ Password reset failed")
            return
        
        # Step 4: Verify token is deleted
        print("\nStep 4: Verifying token cleanup...")
        token_data_after = validate_reset_token(token)
        
        if not token_data_after:
            print("✅ Token properly deleted after use")
        else:
            print("❌ Token still exists after reset")
        
        print("\n" + "=" * 50)
        print("PASSWORD RESET WORKFLOW TEST COMPLETE")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during workflow test: {e}")

def main():
    """Main function to run the demo"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Show console demo
    demo_forgot_password_system()
    test_password_reset_workflow()
    
    # Show GUI demo
    window = ForgotPasswordDemoWindow()
    window.show()
    
    print("\n" + "=" * 70)
    print("GUI DEMO STARTED")
    print("=" * 70)
    print("Use the buttons to test the forgot password system!")
    print("=" * 70)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
