import os
import json
from PyQt6 import QtWidgets, QtCore, QtGui

# Import email verification
try:
    from email_verification import verification_manager, is_verified, resend_verification
except ImportError:
    print("Warning: email_verification not found, verification popup disabled")
    verification_manager = None

# Import real email service
try:
    from email_service import send_verification_email
except ImportError:
    print("Warning: email_service not found, using fallback")
    send_verification_email = None

class VerificationPopup(QtWidgets.QDialog):
    """Modern popup dialog for email verification during login"""
    
    def __init__(self, parent=None, username: str = "", email: str = ""):
        super().__init__(parent)
        self.username = username
        self.email = email
        self.verification_sent = False
        self.resend_count = 0
        self.countdown_seconds = 0
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the modern verification popup UI"""
        self.setWindowTitle("Email Verification Required")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.setWindowFlags(QtCore.Qt.WindowType.Dialog | QtCore.Qt.WindowType.FramelessWindowHint)
        
        # Create main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with icon
        header_layout = QtWidgets.QHBoxLayout()
        
        # Email icon (using a simple circle for now)
        icon_label = QtWidgets.QLabel("📧")
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title
        title = QtWidgets.QLabel("Email Verification Required")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2c3e50;
            margin-left: 15px;
        """)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Message
        message = QtWidgets.QLabel(
            f"Your account <b>{self.username}</b> is not verified.\n\n"
            f"Would you like us to send a verification link to your email now?"
        )
        message.setStyleSheet("""
            font-size: 14px; 
            color: #34495e;
            line-height: 1.4;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        """)
        message.setWordWrap(True)
        message.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(message)
        
        # Email display
        if self.email:
            email_label = QtWidgets.QLabel(f"📧 {self.email}")
            email_label.setStyleSheet("""
                font-size: 12px; 
                color: #7f8c8d;
                font-style: italic;
                padding: 5px 15px;
            """)
            layout.addWidget(email_label)
        
        # Status label (initially hidden)
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("""
            font-size: 13px;
            padding: 10px 15px;
            border-radius: 6px;
            margin: 10px 0;
        """)
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Countdown label (initially hidden)
        self.countdown_label = QtWidgets.QLabel("")
        self.countdown_label.setStyleSheet("""
            font-size: 12px;
            padding: 8px 15px;
            border-radius: 6px;
            margin: 5px 0;
            background-color: #fff3cd;
            color: #856404;
            border-left: 4px solid #ffc107;
        """)
        self.countdown_label.setWordWrap(True)
        self.countdown_label.hide()
        layout.addWidget(self.countdown_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(15)
        
        # No button
        self.no_button = QtWidgets.QPushButton("No, Thanks")
        self.no_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.no_button.clicked.connect(self.reject)
        button_layout.addWidget(self.no_button)
        
        # Yes button
        self.yes_button = QtWidgets.QPushButton("Yes, Send Email")
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.yes_button.clicked.connect(self._send_verification_email)
        button_layout.addWidget(self.yes_button)
        
        # Resend button (initially hidden)
        self.resend_button = QtWidgets.QPushButton("Resend Email")
        self.resend_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.resend_button.clicked.connect(self._resend_verification_email)
        self.resend_button.hide()
        button_layout.addWidget(self.resend_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing at the bottom
        layout.addStretch()
        
        # Set window background
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 12px;
            }
        """)
        
        # Center the dialog
        self._center_dialog()
    
    def _center_dialog(self):
        """Center the dialog on the parent window"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _connect_signals(self):
        """Connect signals"""
        pass
    
    def _send_verification_email(self):
        """Send verification email and show confirmation"""
        if not verification_manager:
            self._show_status("❌ Email verification system not available", "error")
            return
        
        try:
            # Generate new verification token
            new_token = resend_verification(self.username, 24)
            print(f"DEBUG: Generated new verification token for {self.username}")
            
            # Send verification email using real email service
            email_sent = False
            if send_verification_email:
                email_sent = send_verification_email(self.username, self.email, new_token)
                print(f"DEBUG: Real email service result: {email_sent}")
            else:
                # Fallback to simulation if real email service not available
                from email_verification import send_verification_email_simulation
                email_sent = send_verification_email_simulation(self.username, self.email, new_token)
                print(f"DEBUG: Fallback email simulation result: {email_sent}")
            
            if email_sent:
                self.verification_sent = True
                self.resend_count += 1
                
                # Calculate countdown time (increases with each resend to prevent spam)
                # Progression: 30s, 1m, 5m, 10m, then stays at 10m
                countdown_progression = [30, 60, 300, 600]  # 30s, 1m, 5m, 10m
                if self.resend_count <= len(countdown_progression):
                    self.countdown_seconds = countdown_progression[self.resend_count - 1]
                else:
                    self.countdown_seconds = 600  # Stay at 10m for subsequent resends
                
                self._show_status(
                    f"✅ Verification email sent successfully!\n\n"
                    f"Please check your email at {self.email} and click the verification link.\n"
                    f"You can then return to login.",
                    "success"
                )
                
                # Start countdown
                self._start_countdown()
                
                # Update buttons
                self.yes_button.hide()
                self.resend_button.show()
                self.resend_button.setEnabled(False)
                
                # Change No button to Close
                self.no_button.setText("Close")
                
            else:
                self._show_status("❌ Failed to send verification email. Please try again.", "error")
                
        except Exception as e:
            print(f"Error sending verification email: {e}")
            self._show_status("❌ Error sending verification email. Please try again.", "error")
    
    def _show_status(self, message: str, status_type: str):
        """Show status message with appropriate styling"""
        self.status_label.setText(message)
        
        if status_type == "success":
            self.status_label.setStyleSheet("""
                font-size: 13px;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 10px 0;
                background-color: #d5f4e6;
                color: #27ae60;
                border-left: 4px solid #27ae60;
            """)
        elif status_type == "error":
            self.status_label.setStyleSheet("""
                font-size: 13px;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 10px 0;
                background-color: #fadbd8;
                color: #e74c3c;
                border-left: 4px solid #e74c3c;
            """)
        else:
            self.status_label.setStyleSheet("""
                font-size: 13px;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 10px 0;
                background-color: #f8f9fa;
                color: #34495e;
                border-left: 4px solid #3498db;
            """)
        
        self.status_label.show()
    
    def _start_countdown(self):
        """Start the countdown timer"""
        self.countdown_timer.start(1000)  # Update every second
        self._update_countdown()
    
    def _update_countdown(self):
        """Update the countdown display"""
        if self.countdown_seconds > 0:
            minutes = self.countdown_seconds // 60
            seconds = self.countdown_seconds % 60
            
            if minutes > 0:
                time_str = f"{minutes}m {seconds:02d}s"
            else:
                time_str = f"{seconds}s"
            
            self.countdown_label.setText(
                f"⏰ Resend available in {time_str}\n"
                f"📧 Email sent to {self.email}"
            )
            self.countdown_label.show()
            
            self.countdown_seconds -= 1
        else:
            # Countdown finished
            self.countdown_timer.stop()
            self.countdown_label.hide()
            self.resend_button.setEnabled(True)
            self.resend_button.setText("Resend Email")
    
    def _resend_verification_email(self):
        """Resend verification email"""
        if self.countdown_seconds > 0:
            return  # Still in countdown
        
        # Calculate countdown time for next resend (same progression)
        # Progression: 30s, 1m, 5m, 10m, then stays at 10m
        countdown_progression = [30, 60, 300, 600]  # 30s, 1m, 5m, 10m
        if self.resend_count + 1 <= len(countdown_progression):
            self.countdown_seconds = countdown_progression[self.resend_count]
        else:
            self.countdown_seconds = 600  # Stay at 10m for subsequent resends
        
        self._start_countdown()
        
        # Send email again
        self._send_verification_email()
    
    def get_verification_sent(self) -> bool:
        """Return whether verification email was sent"""
        return self.verification_sent


def show_verification_popup(parent=None, username: str = "", email: str = "") -> bool:
    """
    Show the verification popup dialog
    
    Args:
        parent: Parent window
        username: Username to verify
        email: Email address to send verification to
        
    Returns:
        bool: True if verification email was sent, False otherwise
    """
    dialog = VerificationPopup(parent, username, email)
    result = dialog.exec()
    
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        return dialog.get_verification_sent()
    return False


def get_user_email(username: str) -> str:
    """Get user's email using hybrid user manager with case-insensitive lookup"""
    try:
        # Try hybrid user manager first
        from hybrid_user_manager import get_user_case_insensitive
        user_data = get_user_case_insensitive(username)
        if user_data:
            return user_data.get("email", "")
    except ImportError:
        pass
    
    # Fallback to old JSON method
    try:
        users_path = os.path.join(os.path.dirname(__file__), "users.json")
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            users = data.get("users", {})
            return users.get(username, {}).get("email", "")
    except Exception as e:
        print(f"Error reading user email: {e}")
    return ""


if __name__ == "__main__":
    import sys
    from PyQt6 import QtWidgets
    
    app = QtWidgets.QApplication(sys.argv)
    dialog = VerificationPopup(username="testuser", email="test@example.com")
    dialog.show()
    sys.exit(app.exec())
