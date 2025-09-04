import os
from PyQt6 import QtWidgets, uic, QtCore, QtGui

# Import email verification
try:
    from email_verification import verification_manager, verify_email, is_verified, resend_verification, send_verification_email_simulation
except ImportError:
    print("Warning: email_verification not found, verification dialog disabled")
    verification_manager = None

class VerificationDialog(QtWidgets.QDialog):
    """Dialog for email verification"""
    
    def __init__(self, parent=None, username: str = "", email: str = ""):
        super().__init__(parent)
        self.username = username
        self.email = email
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the verification dialog UI"""
        self.setWindowTitle("Email Verification")
        self.setModal(True)
        self.resize(500, 400)
        
        # Create main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("Email Verification")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QtWidgets.QLabel(
            "Please enter your verification details below:"
        )
        instructions.setStyleSheet("margin: 10px;")
        layout.addWidget(instructions)
        
        # Username field
        username_layout = QtWidgets.QHBoxLayout()
        username_layout.addWidget(QtWidgets.QLabel("Username:"))
        self.username_field = QtWidgets.QLineEdit()
        self.username_field.setText(self.username)
        self.username_field.setPlaceholderText("Enter your username")
        username_layout.addWidget(self.username_field)
        layout.addLayout(username_layout)
        
        # Token field
        token_layout = QtWidgets.QHBoxLayout()
        token_layout.addWidget(QtWidgets.QLabel("Verification Token:"))
        self.token_field = QtWidgets.QLineEdit()
        self.token_field.setPlaceholderText("Enter verification token from email")
        token_layout.addWidget(self.token_field)
        layout.addWidget(QtWidgets.QLabel("Verification Token:"))
        layout.addWidget(self.token_field)
        
        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("margin: 10px; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.verify_button = QtWidgets.QPushButton("Verify Email")
        self.verify_button.clicked.connect(self._verify_email)
        button_layout.addWidget(self.verify_button)
        
        self.resend_button = QtWidgets.QPushButton("Resend Email")
        self.resend_button.clicked.connect(self._resend_email)
        button_layout.addWidget(self.resend_button)
        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Check if user is already verified
        if self.username and verification_manager:
            if is_verified(self.username):
                self._show_status("✅ Your email is already verified!", "green")
                self.verify_button.setEnabled(False)
                self.resend_button.setEnabled(False)
    
    def _connect_signals(self):
        """Connect signals"""
        self.username_field.textChanged.connect(self._on_username_changed)
        self.token_field.returnPressed.connect(self._verify_email)
    
    def _on_username_changed(self):
        """Handle username field changes"""
        username = self.username_field.text().strip()
        if username and verification_manager:
            if is_verified(username):
                self._show_status("✅ This user is already verified!", "green")
                self.verify_button.setEnabled(False)
                self.resend_button.setEnabled(True)
            else:
                self._show_status("❌ This user is not verified yet.", "orange")
                self.verify_button.setEnabled(True)
                self.resend_button.setEnabled(True)
        else:
            self._clear_status()
            self.verify_button.setEnabled(True)
            self.resend_button.setEnabled(False)
    
    def _verify_email(self):
        """Verify the email with the provided token"""
        if not verification_manager:
            self._show_status("❌ Email verification system not available", "red")
            return
        
        username = self.username_field.text().strip()
        token = self.token_field.text().strip()
        
        if not username:
            self._show_status("❌ Please enter your username", "red")
            return
        
        if not token:
            self._show_status("❌ Please enter the verification token", "red")
            return
        
        # Verify the email
        if verify_email(username, token):
            self._show_status("✅ Email verified successfully!", "green")
            self.verify_button.setEnabled(False)
            self.resend_button.setEnabled(False)
            
            # Show success message
            QtWidgets.QMessageBox.information(
                self,
                "Verification Successful",
                f"Your email has been verified successfully!\n\n"
                f"You can now login to your account."
            )
        else:
            self._show_status("❌ Verification failed. Please check your token.", "red")
    
    def _resend_email(self):
        """Resend verification email"""
        if not verification_manager:
            self._show_status("❌ Email verification system not available", "red")
            return
        
        username = self.username_field.text().strip()
        
        if not username:
            self._show_status("❌ Please enter your username", "red")
            return
        
        # Check if user exists in users.json
        try:
            users_path = os.path.join(os.path.dirname(__file__), "users.json")
            if os.path.exists(users_path):
                import json
                with open(users_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                users = data.get("users", {})
                
                if username not in users:
                    self._show_status("❌ Username not found", "red")
                    return
                
                email = users[username].get("email", "")
                if not email:
                    self._show_status("❌ No email found for this user", "red")
                    return
                
                # Generate new verification token
                new_token = resend_verification(username, 24)
                
                # Send verification email (simulation)
                if send_verification_email_simulation(username, email, new_token):
                    self._show_status("✅ Verification email sent!", "green")
                else:
                    self._show_status("❌ Failed to send verification email", "red")
            else:
                self._show_status("❌ User database not found", "red")
        except Exception as e:
            print(f"Error resending verification email: {e}")
            self._show_status("❌ Error resending email", "red")
    
    def _show_status(self, message: str, color: str):
        """Show status message with color"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"margin: 10px; padding: 10px; border-radius: 5px; background-color: {color}; color: white;")
    
    def _clear_status(self):
        """Clear status message"""
        self.status_label.setText("")
        self.status_label.setStyleSheet("margin: 10px; padding: 10px; border-radius: 5px;")


def show_verification_dialog(parent=None, username: str = "", email: str = ""):
    """Show the verification dialog"""
    dialog = VerificationDialog(parent, username, email)
    return dialog.exec()


if __name__ == "__main__":
    import sys
    from PyQt6 import QtWidgets
    
    app = QtWidgets.QApplication(sys.argv)
    dialog = VerificationDialog()
    dialog.show()
    sys.exit(app.exec())
