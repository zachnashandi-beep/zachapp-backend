#!/usr/bin/env python3
"""
Reset Password Dialog
Dialog for resetting password with token
"""

import sys
import re
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from password_reset_manager import validate_reset_token, reset_password

class ResetPasswordDialog(QtWidgets.QDialog):
    """Dialog for resetting password with token"""
    
    def __init__(self, token: str = None, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("Reset Password")
        self.setModal(True)
        self.setFixedSize(800, 750)  # Increased size for better visibility
        
        # Set window icon if available
        try:
            self.setWindowIcon(QtGui.QIcon("emoji/hidden.png"))
        except:
            pass
        
        self._setup_ui()
        self._connect_signals()
        self._apply_styling()
        
        # If token provided, validate it
        if self.token:
            self._validate_token()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(35)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # Title
        title = QtWidgets.QLabel("Reset Your Password")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Token input section (if no token provided)
        if not self.token:
            self.token_label = QtWidgets.QLabel("Reset Token:")
            self.token_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
            """)
            layout.addWidget(self.token_label)
            
            self.token_field = QtWidgets.QLineEdit()
            self.token_field.setPlaceholderText("Enter the reset token from your email")
            self.token_field.setMinimumHeight(50)
            self.token_field.setStyleSheet("""
                QLineEdit {
                    padding: 15px;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    font-size: 16px;
                    background-color: white;
                    color: black;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    color: black;
                }
            """)
            layout.addWidget(self.token_field)
        
        # User info section
        self.user_info_label = QtWidgets.QLabel("Enter a valid reset token to continue")
        self.user_info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.user_info_label.setWordWrap(True)
        self.user_info_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #bdc3c7;
            min-height: 20px;
        """)
        layout.addWidget(self.user_info_label)
        
        # New password section
        self.password_label = QtWidgets.QLabel("New Password:")
        self.password_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #34495e;
        """)
        layout.addWidget(self.password_label)
        
        self.password_field = QtWidgets.QLineEdit()
        self.password_field.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Enter your new password")
        self.password_field.setMinimumHeight(50)
        self.password_field.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 16px;
                background-color: white;
                color: black;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                color: black;
            }
        """)
        layout.addWidget(self.password_field)
        
        # Confirm password section
        self.confirm_label = QtWidgets.QLabel("Confirm New Password:")
        self.confirm_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #34495e;
        """)
        layout.addWidget(self.confirm_label)
        
        self.confirm_field = QtWidgets.QLineEdit()
        self.confirm_field.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.confirm_field.setPlaceholderText("Confirm your new password")
        self.confirm_field.setMinimumHeight(50)
        self.confirm_field.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 16px;
                background-color: white;
                color: black;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                color: black;
            }
        """)
        layout.addWidget(self.confirm_field)
        
        # Password strength indicator
        self.strength_label = QtWidgets.QLabel("")
        self.strength_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.strength_label.setWordWrap(True)
        self.strength_label.setStyleSheet("""
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            min-height: 20px;
        """)
        layout.addWidget(self.strength_label)
        
        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            min-height: 20px;
        """)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.reset_button = QtWidgets.QPushButton("Reset Password")
        self.reset_button.setMinimumHeight(50)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals and slots"""
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button.clicked.connect(self._handle_reset_password)
        self.password_field.textChanged.connect(self._check_password_strength)
        self.confirm_field.textChanged.connect(self._clear_status)
        
        if hasattr(self, 'token_field'):
            self.token_field.textChanged.connect(self._clear_status)
            self.token_field.returnPressed.connect(self._validate_token)
    
    def _apply_styling(self):
        """Apply overall dialog styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
        """)
    
    def _clear_status(self):
        """Clear status message"""
        self.status_label.setText("")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        """)
    
    def _show_status(self, message: str, is_error: bool = False):
        """Show status message"""
        color = "#e74c3c" if is_error else "#27ae60"
        background = "#fdf2f2" if is_error else "#f0f9f0"
        
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            background-color: {background};
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border: 1px solid {color};
        """)
    
    def _validate_token(self):
        """Validate the reset token"""
        if not self.token:
            if hasattr(self, 'token_field'):
                self.token = self.token_field.text().strip()
        
        if not self.token:
            self._show_status("Please enter a reset token.", True)
            self.user_info_label.setText("Enter a valid reset token to continue")
            self.user_info_label.setStyleSheet("""
                font-size: 14px;
                color: #7f8c8d;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #bdc3c7;
                min-height: 20px;
            """)
            return False
        
        # Validate token
        token_data = validate_reset_token(self.token)
        
        if not token_data:
            self._show_status("Invalid or expired reset token.", True)
            self.user_info_label.setText("Invalid or expired reset token")
            self.user_info_label.setStyleSheet("""
                font-size: 14px;
                color: #e74c3c;
                background-color: #fdf2f2;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #e74c3c;
                min-height: 20px;
            """)
            return False
        
        # Show user info
        self.user_info_label.setText(
            f"✅ Resetting password for: {token_data['username']}\n"
            f"📧 Email: {token_data['email']}"
        )
        self.user_info_label.setStyleSheet("""
            font-size: 14px;
            color: #27ae60;
            background-color: #f0f9f0;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #27ae60;
            min-height: 20px;
        """)
        
        # Enable password fields
        self.password_field.setEnabled(True)
        self.confirm_field.setEnabled(True)
        self.reset_button.setEnabled(True)
        
        return True
    
    def _check_password_strength(self, password: str):
        """Check password strength and display indicator"""
        if not password:
            self.strength_label.setText("")
            return
        
        # Simple strength check (reuse from signup)
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        length = len(password)
        
        # Calculate strength score
        score = 0
        if length >= 6:
            score += 1
        if length >= 8:
            score += 1
        if has_upper:
            score += 1
        if has_lower:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1
        
        # Determine strength level
        if score <= 2:
            strength = "Weak"
            color = "#e74c3c"
        elif score <= 4:
            strength = "Medium"
            color = "#f39c12"
        else:
            strength = "Strong"
            color = "#27ae60"
        
        self.strength_label.setText(f"Password Strength: {strength}")
        self.strength_label.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            font-weight: bold;
            padding: 5px;
            border-radius: 3px;
            margin: 5px 0;
        """)
    
    def _handle_reset_password(self):
        """Handle password reset"""
        if not self.token:
            if hasattr(self, 'token_field'):
                if not self._validate_token():
                    return
        
        new_password = self.password_field.text()
        confirm_password = self.confirm_field.text()
        
        if not new_password:
            self._show_status("Please enter a new password.", True)
            return
        
        if new_password != confirm_password:
            self._show_status("Passwords do not match.", True)
            return
        
        # Check password strength
        strength, _ = self._check_password_strength(new_password)
        if strength == "Weak":
            self._show_status("Password must be at least Medium strength.", True)
            return
        
        # Reset password
        success = reset_password(self.token, new_password)
        
        if success:
            self._show_status("Password reset successfully! You can now log in with your new password.")
            
            # Disable form
            self.password_field.setEnabled(False)
            self.confirm_field.setEnabled(False)
            self.reset_button.setEnabled(False)
            
            # Change button text
            self.reset_button.setText("Success!")
            self.reset_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            
            # Auto-close after 3 seconds
            QtCore.QTimer.singleShot(3000, self.accept)
        else:
            self._show_status("Failed to reset password. Token may be invalid or expired.", True)

def show_reset_password_dialog(token: str = None, parent=None):
    """Show the reset password dialog"""
    dialog = ResetPasswordDialog(token, parent)
    return dialog.exec()

if __name__ == "__main__":
    # Demo the reset password dialog
    app = QtWidgets.QApplication(sys.argv)
    
    # Test with a sample token (this will fail validation)
    dialog = ResetPasswordDialog("sample_token")
    result = dialog.exec()
    
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        print("Password reset successful")
    else:
        print("Password reset cancelled")
    
    sys.exit(0)
