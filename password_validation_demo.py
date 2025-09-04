#!/usr/bin/env python3
"""
Password Validation Demo
Demonstrates the simplified password validation (6+ characters only)
"""

import sys
import os
from PyQt6 import QtWidgets, QtCore, QtGui

# Import the signup dialog
try:
    from signup import SignupDialog
except ImportError:
    print("Error: Could not import SignupDialog")
    sys.exit(1)

class PasswordValidationDemoWindow(QtWidgets.QMainWindow):
    """Demo window to test password validation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Validation Demo")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add title
        title = QtWidgets.QLabel("Password Validation Demo")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        """)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add instructions
        instructions = QtWidgets.QLabel("""
                 <h3>Password Strength Requirements:</h3>
         <ul>
             <li>✅ <b>Medium strength</b> or higher required for signup</li>
             <li>🔴 <b>Weak:</b> Score ≤ 2 (too simple)</li>
             <li>🟠 <b>Medium:</b> Score 3-4 (acceptable)</li>
             <li>🟢 <b>Strong:</b> Score 5-6 (excellent)</li>
         </ul>
         
         <h3>Strength Factors:</h3>
         <ul>
             <li>Length ≥ 6 characters (+1 point)</li>
             <li>Length ≥ 8 characters (+1 point)</li>
             <li>Contains uppercase letter (+1 point)</li>
             <li>Contains lowercase letter (+1 point)</li>
             <li>Contains number (+1 point)</li>
             <li>Contains special character (+1 point)</li>
         </ul>
         
         <h3>Examples:</h3>
         <ul>
             <li><b>Medium:</b> "password", "123456", "Hello1"</li>
             <li><b>Strong:</b> "Password123", "MyPass1!", "hello123"</li>
             <li><b>Weak:</b> "12345", "abc", "pass"</li>
         </ul>
        
        <h3>Instructions:</h3>
        <ol>
            <li>Click "Open Signup Form" to test password validation</li>
            <li>Try passwords with different strength levels</li>
            <li>Watch the strength indicator change as you type</li>
            <li>Only Medium or Strong passwords can be used to sign up</li>
        </ol>
        """)
        instructions.setStyleSheet("""
            font-size: 14px;
            color: #34495e;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin: 10px;
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Add button to open signup form
        self.open_button = QtWidgets.QPushButton("Open Signup Form")
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.open_button.clicked.connect(self.open_signup_form)
        layout.addWidget(self.open_button)
        
        # Add status label
        self.status_label = QtWidgets.QLabel("Ready to test password validation")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            padding: 10px;
            text-align: center;
        """)
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Add some spacing
        layout.addStretch()
    
    def open_signup_form(self):
        """Open the signup form for testing"""
        try:
            self.status_label.setText("Opening signup form...")
            self.status_label.setStyleSheet("""
                font-size: 12px;
                color: #f39c12;
                padding: 10px;
                text-align: center;
            """)
            
            # Create and show signup dialog
            signup_dialog = SignupDialog(self)
            signup_dialog.exec()
            
            self.status_label.setText("Signup form closed. Ready to test again.")
            self.status_label.setStyleSheet("""
                font-size: 12px;
                color: #27ae60;
                padding: 10px;
                text-align: center;
            """)
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("""
                font-size: 12px;
                color: #e74c12;
                padding: 10px;
                text-align: center;
            """)

def demo_password_validation():
    """Demonstrate password validation functionality"""
    print("=" * 70)
    print("PASSWORD VALIDATION DEMO")
    print("=" * 70)
    
    print("\n1. Password Strength Requirements:")
    print("   ✅ Medium strength or higher required for signup")
    print("   🔴 Weak: Score ≤ 2 (too simple)")
    print("   🟠 Medium: Score 3-4 (acceptable)")
    print("   🟢 Strong: Score 5-6 (excellent)")
    
    print("\n2. Strength Factors (6 total points possible):")
    print("   • Length ≥ 6 characters (+1 point)")
    print("   • Length ≥ 8 characters (+1 point)")
    print("   • Contains uppercase letter (+1 point)")
    print("   • Contains lowercase letter (+1 point)")
    print("   • Contains number (+1 point)")
    print("   • Contains special character (+1 point)")
    
    print("\n3. Examples of Medium+ Passwords (can sign up):")
    print("   🟠 'password' (8 chars + lowercase = 3 points)")
    print("   🟠 '123456' (6 chars = 1 point, but needs more)")
    print("   🟠 'Hello1' (6 chars + upper + lower + digit = 4 points)")
    print("   🟢 'Password123' (8 chars + upper + lower + digit = 5 points)")
    
    print("\n4. Examples of Weak Passwords (cannot sign up):")
    print("   🔴 '12345' (5 chars = 0 points)")
    print("   🔴 'abc' (3 chars = 0 points)")
    print("   🔴 'pass' (4 chars = 0 points)")
    
    print("\n5. Benefits of Strength-Based System:")
    print("   ✅ Flexible requirements (Medium instead of Strong)")
    print("   ✅ Clear visual feedback (Weak/Medium/Strong)")
    print("   ✅ Balanced security and usability")
    print("   ✅ Users can choose their preferred complexity level")
    
    print("\n6. Technical Changes:")
    print("   ✅ Restored strength-based validation")
    print("   ✅ Updated signup requirement to Medium strength")
    print("   ✅ Improved scoring system (6-point scale)")
    print("   ✅ Better user experience with clear feedback")
    
    print("\n" + "=" * 70)
    print("PASSWORD VALIDATION DEMO COMPLETE")
    print("=" * 70)

def test_password_validation():
    """Test password validation with sample passwords"""
    print("\n" + "=" * 70)
    print("PASSWORD VALIDATION TESTS")
    print("=" * 70)
    
    # Import the signup dialog to test validation
    try:
        from signup import SignupDialog
        
        # Create a temporary dialog to test validation
        dialog = SignupDialog()
        
        test_passwords = [
            ("password", True, "8 chars + lowercase = Medium"),
            ("123456", False, "6 chars only = Weak"),
            ("Hello1", True, "6 chars + upper + lower + digit = Medium"),
            ("Password123", True, "8 chars + upper + lower + digit = Strong"),
            ("MyPass1!", True, "8 chars + all factors = Strong"),
            ("12345", False, "5 chars = Weak"),
            ("abc", False, "3 chars = Weak"),
            ("pass", False, "4 chars = Weak"),
            ("", False, "empty = Weak"),
        ]
        
        print("\nTesting password validation:")
        print("-" * 50)
        
        for password, expected, description in test_passwords:
            strength, color = dialog._check_password_strength(password)
            is_valid = strength != "Weak"  # Medium or Strong is valid
            status = "✅ PASS" if is_valid == expected else "❌ FAIL"
            print(f"{password:12} → {strength:6} | {description:35} | {status}")
        
        print("-" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error testing password validation: {e}")

def main():
    """Main function to run the demo"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Show console demo
    demo_password_validation()
    test_password_validation()
    
    # Show GUI demo
    window = PasswordValidationDemoWindow()
    window.show()
    
    print("\n" + "=" * 70)
    print("GUI DEMO STARTED")
    print("=" * 70)
    print("Click 'Open Signup Form' to test the new password validation!")
    print("=" * 70)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
