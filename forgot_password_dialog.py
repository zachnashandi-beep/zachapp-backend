#!/usr/bin/env python3
"""
Forgot Password Dialog
Dialog for requesting password reset
"""

import sys
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from password_reset_manager import generate_reset_token
from email_service import send_reset_email

class ForgotPasswordDialog(QtWidgets.QDialog):
    """Dialog for requesting password reset"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setModal(True)
        self.setFixedSize(550, 450)
        
        self.send_timer = None
        self.send_countdown = 0
        
        # Set window icon if available
        try:
            self.setWindowIcon(QtGui.QIcon("emoji/hidden.png"))
        except:
            pass
        
        self._setup_ui()
        self._connect_signals()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QtWidgets.QLabel("Forgot Password?")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Description
        description = QtWidgets.QLabel("""
        Enter your username or email address and we'll send you a link to reset your password.
        """)
        description.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 20px;
        """)
        layout.addWidget(description)
        
        # Input field
        self.input_label = QtWidgets.QLabel("Username or Email:")
        self.input_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #34495e;
        """)
        layout.addWidget(self.input_label)
        
        self.input_field = QtWidgets.QLineEdit()
        self.input_field.setPlaceholderText("Enter your username or email address")
        self.input_field.setMinimumHeight(60)
        self.input_field.setStyleSheet("""
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
        layout.addWidget(self.input_field)
        
        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            min-height: 30px;
        """)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.send_button = QtWidgets.QPushButton("Send Reset Link")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        button_layout.addWidget(self.send_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals and slots"""
        self.cancel_button.clicked.connect(self.reject)
        self.send_button.clicked.connect(self._handle_send_reset)
        self.input_field.returnPressed.connect(self._handle_send_reset)
        self.input_field.textChanged.connect(self._clear_status)
    
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
    
    def _handle_send_reset(self):
        """Handle send reset link request"""
        username_or_email = self.input_field.text().strip()
        
        if not username_or_email:
            self._show_status("Please enter your username or email address.", True)
            return
        
        # Generate reset token
        token = generate_reset_token(username_or_email)
        
        if not token:
            self._show_status("No account found with that username or email address.", True)
            return
        
        # Load user info to get email
        import json
        try:
            with open("users.json", 'r') as f:
                users = json.load(f)
            
            user_email = None
            username = None
            for user_data in users.values():
                if (user_data.get('username') == username_or_email or 
                    user_data.get('email') == username_or_email):
                    user_email = user_data.get('email')
                    username = user_data.get('username')
                    break
            
            if user_email and username:
                # Send reset email (real email)
                email_sent = send_reset_email(username, user_email, token)
                
                if email_sent:
                    self._show_status(
                        f"✅ Password reset link sent to {user_email}!\n\n"
                        f"📧 Please check your email and click the link to reset your password.\n"
                        f"⏰ The link will expire in 1 hour.\n\n"
                        f"💡 If you don't see the email, check your spam folder."
                    )
                else:
                    self._show_status(
                        f"❌ Failed to send email to {user_email}.\n\n"
                        f"Please check your email address and try again.\n"
                        f"If the problem persists, contact support.",
                        True
                    )
                
                # Disable send button and start countdown timer
                self.send_button.setEnabled(False)
                self.send_countdown = 30  # 30 second cooldown
                self._update_send_button_text()
                
                # Start countdown timer
                self.send_timer = QtCore.QTimer()
                self.send_timer.timeout.connect(self._update_countdown)
                self.send_timer.start(1000)  # Update every second
                
                # Timer will handle re-enabling the send button
            else:
                self._show_status("Error retrieving user information.", True)
                
        except Exception as e:
            self._show_status(f"Error: {str(e)}", True)
    
    def _update_countdown(self):
        """Update the countdown timer"""
        self.send_countdown -= 1
        self._update_send_button_text()
        
        if self.send_countdown <= 0:
            self.send_timer.stop()
            self.send_button.setEnabled(True)
            self.send_button.setText("Send Reset Link")
    
    def _update_send_button_text(self):
        """Update the send button text with countdown"""
        if self.send_countdown > 0:
            self.send_button.setText(f"Resend in {self.send_countdown}s")
        else:
            self.send_button.setText("Send Reset Link")
    

def show_forgot_password_dialog(parent=None):
    """Show the forgot password dialog"""
    dialog = ForgotPasswordDialog(parent)
    return dialog.exec()

if __name__ == "__main__":
    # Demo the forgot password dialog
    app = QtWidgets.QApplication(sys.argv)
    
    dialog = ForgotPasswordDialog()
    result = dialog.exec()
    
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog cancelled")
    
    sys.exit(0)
