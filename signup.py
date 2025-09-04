import os, re, hashlib, json
from PyQt6 import QtWidgets, uic, QtCore, QtGui

# Import email verification
try:
    from email_verification import verification_manager, generate_verification_token, send_verification_email_simulation
except ImportError:
    print("Warning: email_verification not found, email verification disabled")
    verification_manager = None

# Import Caps Lock indicator
try:
    from capslock_indicator import setup_capslock_detection
except ImportError:
    print("Warning: capslock_indicator not found, Caps Lock detection disabled")
    setup_capslock_detection = None

class SignupDialog(QtWidgets.QDialog):
    # Signal emitted on successful signup with (username, password_hash, email)
    signupCompleted = QtCore.pyqtSignal(str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._setup_ui()
        self._connect_signals()
        self._load_profanity_list()
    
    def _load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), "Signup.ui")
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Create Account")
        except Exception as e:
            raise RuntimeError(f"Failed to load Signup.ui: {e}")
    
    def _setup_ui(self):
        """Initialize UI state"""
        # Find all widgets
        self.username = self.findChild(QtWidgets.QLineEdit, "UserameSignup")
        self.email = self.findChild(QtWidgets.QLineEdit, "EmailSignup")
        self.password = self.findChild(QtWidgets.QLineEdit, "PassSignup")
        self.confirm = self.findChild(QtWidgets.QLineEdit, "ReEnterPass")
        self.signup = self.findChild(QtWidgets.QPushButton, "Signup")
        self.strength = self.findChild(QtWidgets.QLabel, "PasswordStrength")
        self.username_notice = self.findChild(QtWidgets.QLabel, "UsernameNotice")
        self.email_notice = self.findChild(QtWidgets.QLabel, "EmailNotice")
        self.capslock_label = self.findChild(QtWidgets.QLabel, "CapsLock")
        
        # Mask passwords
        if self.password:
            self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        if self.confirm:
            self.confirm.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            
        # Clear notices
        if self.username_notice:
            self.username_notice.setText("")
        if self.email_notice:
            self.email_notice.setText("")
        
        # Setup Caps Lock indicator
        if setup_capslock_detection and self.capslock_label:
            password_fields = [self.password, self.confirm]
            self.capslock_indicator, self.capslock_event_filter = setup_capslock_detection(
                password_fields, self.capslock_label
            )
        if self.strength:
            self.strength.setText("")
            
        # Disable signup initially
        if self.signup:
            self.signup.setEnabled(False)

    def _connect_signals(self):
        """Wire up all field validations"""
        if self.username:
            self.username.textChanged.connect(self._validate_username_live)
        if self.email:
            self.email.textChanged.connect(self._validate_email_live)
        if self.password:
            self.password.textChanged.connect(self._validate_password_live)
        if self.confirm:
            self.confirm.textChanged.connect(self._validate_form)
        if self.signup:
            self.signup.clicked.connect(self._handle_signup)
        
        # Caps Lock detection is handled by the modular indicator
        
        # Connect "Already have an account?" link
        alr_account = self.findChild(QtWidgets.QLabel, "AlrAccount")
        if alr_account:
            alr_account.setText('<a href="#">Already have an account? Login</a>')
            alr_account.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
            alr_account.setOpenExternalLinks(False)
            alr_account.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            alr_account.linkActivated.connect(self._go_to_login)
    
    def _go_to_login(self):
        """Close signup dialog to return to login"""
        self.reject()  # Close signup dialog
    
    def _check_password_strength(self, password: str) -> tuple[str, str]:
        if not password:
            return "", ""
            
        # Check password strength based on various criteria
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
            return "Weak", "red"
        elif score <= 4:
            return "Medium", "orange"
        else:
            return "Strong", "green"
    
    def _validate_email(self, email: str) -> bool:
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _load_profanity_list(self):
        """Load comprehensive list of prohibited words"""
        self.prohibited_words = set([
            # Core profanity - single words only
            "fuck", "fucking", "fucked", "fucker", "fucks",
            "shit", "shitting", "shitted", "shitter", "shits",
            "bitch", "bitches", "bitching", "bitched",
            "cunt", "cunts", "cunting", "cunted",
            "asshole", "assholes",
            "cock", "cocks", "cocksucker", "cocksuckers",
            "dick", "dicks", "dickhead", "dickheads",
            "pussy", "pussies",
            "whore", "whores", "whoring", "whored",
            "slut", "sluts", "slutting", "slutty",
            "bastard", "bastards",
            "motherfucker", "motherfuckers",
            "piss", "pissing", "pissed", "pisser", "pisses",
            "tits", "titties", "titty",
            "boob", "boobs", "boobies",
            "porn", "porno", "pornography",
            "rape", "raping", "raped", "rapist",
            "nazi", "hitler",
            "nigga", "nigger", "negro",
            "chink", "gook", "spic", "wetback",
            "terrorist", "terrorism", "bomb", "bombing",
            "fag", "faggot", "fags",
            # Additional offensive terms
            "damn", "damned", "damning",
            "hell", "hells",
            "sex", "sexual", "sexy", "sexing",
            "nude", "nudes", "naked", "nudity",
            "kill", "killing", "killed", "killer", "murder",
            "die", "dying", "died", "death", "dead",
            "hate", "hating", "hated", "hater",
            "stupid", "idiot", "moron", "retard", "retarded",
            "gay", "lesbian",
            "jew", "jewish",
            "drug", "drugs", "cocaine", "heroin", "marijuana",
            "alcohol", "drunk", "drinking", "beer", "wine",
            "cigarette", "smoking", "smoke", "tobacco"
        ])
    
    def _normalize_username(self, username: str) -> str:
        """Normalize username for profanity checking"""
        # Convert to lowercase
        normalized = username.lower()
        
        # Remove dots and underscores
        normalized = normalized.replace('.', '').replace('_', '')
        
        # Replace common obfuscations
        obfuscation_map = {
            '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '6': 'g', '7': 't', '8': 'b', '9': 'g',
            '@': 'a', '$': 's', '!': 'i', '+': 't', '|': 'i'
        }
        
        for char, replacement in obfuscation_map.items():
            normalized = normalized.replace(char, replacement)
        
        return normalized
    
    def _load_users(self) -> dict:
        """Load existing users from users.json"""
        try:
            users_path = os.path.join(os.path.dirname(__file__), "users.json")
            if not os.path.exists(users_path):
                return {}
            with open(users_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("users", {}) if isinstance(data, dict) else {}
        except Exception as e:
            print(f"Warning: failed to load users.json: {e}")
            return {}
    
    def _is_username_available(self, username: str) -> bool:
        """Check if username is available (not already taken)"""
        if not username:
            return False
        users = self._load_users()
        return username.lower() not in [user.lower() for user in users.keys()]
    
    def is_valid_username(self, username: str) -> bool:
        """
        Returns False if:
        - The username starts or ends with '.' or '_'
        - The username contains characters outside [a-zA-Z0-9._]
        - The username contains a blacklisted word (including obfuscated versions)
        - The username is already taken
        Otherwise, returns True
        """
        if not username:
            return False
            
        # Check for invalid start/end characters
        if username.startswith('.') or username.endswith('.') or \
           username.startswith('_') or username.endswith('_'):
            return False
            
        # Check for invalid characters (only allow letters, numbers, dots, underscores)
        if not re.match(r'^[a-zA-Z0-9._]+$', username):
            return False
            
        # Normalize username and check for profanity
        normalized = self._normalize_username(username)
        
        # Check if any prohibited word appears in the normalized username
        for word in self.prohibited_words:
            if word in normalized:
                return False
        
        # Check if username is available
        if not self._is_username_available(username):
            return False
                
        return True

    def _validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and content with detailed error messages"""
        if not username:
            return False, ""
            
        # Length check
        if len(username) < 3:
            return False, "Username too short (min 3 chars)"
        if len(username) > 30:
            return False, "Username too long (max 30 chars)"
            
        # Check format first
        if username.startswith('.') or username.endswith('.') or \
           username.startswith('_') or username.endswith('_'):
            return False, "Cannot start or end with . or _"
        elif not re.match(r'^[a-zA-Z0-9._]+$', username):
            return False, "Only letters, numbers, dots and underscores allowed"
        
        # Check for profanity
        normalized = self._normalize_username(username)
        for word in self.prohibited_words:
            if word in normalized:
                return False, "Username contains inappropriate language"
        
        # Check availability
        if not self._is_username_available(username):
            return False, "Username is already taken"
            
        return True, "Username is available"

    def _validate_username_live(self):
        """Update username validation notice"""
        if not self.username or not self.username_notice:
            return
            
        username = self.username.text().strip()
        valid, message = self._validate_username(username)
        
        if not username:
            self.username_notice.setText("")
        else:
            self.username_notice.setText(message)
            self.username_notice.setStyleSheet(f"color: {'green' if valid else 'red'};")
        self._validate_form()
    
    def _validate_email_live(self):
        """Show email validation in notice label"""
        if not self.email or not self.email_notice:
            return
        email = self.email.text().strip()
        valid = self._validate_email(email)
        if not email:
            self.email_notice.setText("")
        else:
            message = "Valid email format" if valid else "Invalid email format"
            self.email_notice.setText(message)
            self.email_notice.setStyleSheet(f"color: {'green' if valid else 'red'};")
        self._validate_form()

    def _validate_password_live(self):
        """Show password strength and validate no spaces"""
        if not self.password or not self.strength:
            return
        password = self.password.text()
        
        # Check for spaces first
        if ' ' in password:
            self.strength.setText("Spaces not allowed")
            self.strength.setStyleSheet("color: red;")
            return
            
        # Then check strength
        strength, color = self._check_password_strength(password)
        self.strength.setText(strength)
        self.strength.setStyleSheet(f"color: {color};")
        self._validate_form()
    
    def _validate_form(self):
        """Enable signup button only if all fields are filled"""
        if not all([self.username, self.email, self.password, self.confirm, self.signup]):
            return
            
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        
        # Just check if fields are filled, not if they're valid
        self.signup.setEnabled(
            bool(username and email and password and confirm)
        )

    def _handle_signup(self):
        """Process signup when button clicked - validate and show errors"""
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        
        # Validate username
        username_valid, username_msg = self._validate_username(username)
        if not username_valid:
            QtWidgets.QMessageBox.warning(self, "Invalid Username", username_msg)
            return
        
        # Validate email
        email_valid = self._validate_email(email)
        if not email_valid:
            QtWidgets.QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address")
            return
        
        # Validate password
        if ' ' in password:
            QtWidgets.QMessageBox.warning(self, "Invalid Password", "Spaces are not allowed in password")
            return
        
        strength, _ = self._check_password_strength(password)
        if strength == "Weak":
            QtWidgets.QMessageBox.warning(self, "Weak Password", 
                "Password must be at least Medium strength to sign up")
            return
        
        # Validate password match
        if password != confirm:
            QtWidgets.QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return
        
        # All validations passed - emit signup details
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.signupCompleted.emit(username, password_hash, email)
        self.accept()

    def get_signup_data(self) -> tuple[str, str, str]:
        """Return (username, password_hash, email) after successful signup"""
        if self.result() != QtWidgets.QDialog.DialogCode.Accepted:
            return "", "", ""
            
        password = self.password.text()
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        return (
            self.username.text().strip(),
            password_hash,
            self.email.text().strip()
        )
    
    def test_username_validation(self):
        """Test function to demonstrate username validation"""
        test_cases = [
            ("f_ck", False, "profanity"),
            ("sh1t", False, "profanity"),
            ("hello_world", True, "valid"),
            ("_badname", False, "starts with _"),
            ("good.name", True, "valid"),
            ("realbro", True, "valid"),
            ("c.unt", False, "profanity"),
            ("f@ck", False, "profanity"),
            ("user123", True, "valid"),
            ("a", False, "too short"),
            ("", False, "empty"),
            ("user..name", False, "consecutive dots"),
            (".username", False, "starts with dot"),
            ("username.", False, "ends with dot"),
            ("user name", False, "contains space"),
            ("user@name", False, "invalid character")
        ]
        
        print("Username Validation Test Results:")
        print("=" * 50)
        for username, expected, reason in test_cases:
            result = self.is_valid_username(username)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"{username:15} → {result:5} | {reason:20} | {status}")
        
        return True
    
    def _validate_email_live(self):
        """Show email validation in notice label"""
        if not self.email or not self.email_notice:
            return
        email = self.email.text().strip()
        valid = self._validate_email(email)
        if not email:
            self.email_notice.setText("")
        else:
            message = "Valid email format" if valid else "Invalid email format"
            self.email_notice.setText(message)
            self.email_notice.setStyleSheet(f"color: {'green' if valid else 'red'};")
        self._validate_form()

    def _validate_password_live(self):
        """Show password strength and validate no spaces"""
        if not self.password or not self.strength:
            return
        password = self.password.text()
        
        # Check for spaces first
        if ' ' in password:
            self.strength.setText("Spaces not allowed")
            self.strength.setStyleSheet("color: red;")
            return
            
        # Then check strength
        strength, color = self._check_password_strength(password)
        self.strength.setText(strength)
        self.strength.setStyleSheet(f"color: {color};")
        self._validate_form()
    
    def _validate_form(self):
        """Enable signup button only if all fields are filled"""
        if not all([self.username, self.email, self.password, self.confirm, self.signup]):
            return
            
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        
        # Just check if fields are filled, not if they're valid
        self.signup.setEnabled(
            bool(username and email and password and confirm)
        )

    def _handle_signup(self):
        """Process signup when button clicked - validate and show errors"""
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        
        # Validate username
        username_valid, username_msg = self._validate_username(username)
        if not username_valid:
            QtWidgets.QMessageBox.warning(self, "Invalid Username", username_msg)
            return
        
        # Validate email
        email_valid = self._validate_email(email)
        if not email_valid:
            QtWidgets.QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address")
            return
        
        # Validate password
        if ' ' in password:
            QtWidgets.QMessageBox.warning(self, "Invalid Password", "Spaces are not allowed in password")
            return
        
        strength, _ = self._check_password_strength(password)
        if strength == "Weak":
            QtWidgets.QMessageBox.warning(self, "Weak Password", 
                "Password must be at least Medium strength to sign up")
            return
        
        # Validate password match
        if password != confirm:
            QtWidgets.QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return
        
        # All validations passed - emit signup details
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.signupCompleted.emit(username, password_hash, email)
        self.accept()

    def get_signup_data(self) -> tuple[str, str, str]:
        """Return (username, password_hash, email) after successful signup"""
        if self.result() != QtWidgets.QDialog.DialogCode.Accepted:
            return "", "", ""
            
        password = self.password.text()
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        return (
            self.username.text().strip(),
            password_hash,
            self.email.text().strip()
        )
    
    def test_username_validation(self):
        """Test function to demonstrate username validation"""
        test_cases = [
            ("f_ck", False, "profanity"),
            ("sh1t", False, "profanity"),
            ("hello_world", True, "valid"),
            ("_badname", False, "starts with _"),
            ("good.name", True, "valid"),
            ("realbro", True, "valid"),
            ("c.unt", False, "profanity"),
            ("f@ck", False, "profanity"),
            ("user123", True, "valid"),
            ("a", False, "too short"),
            ("", False, "empty"),
            ("user..name", False, "consecutive dots"),
            (".username", False, "starts with dot"),
            ("username.", False, "ends with dot"),
            ("user name", False, "contains space"),
            ("user@name", False, "invalid character")
        ]
        
        print("Username Validation Test Results:")
        print("=" * 50)
        for username, expected, reason in test_cases:
            result = self.is_valid_username(username)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"{username:15} → {result:5} | {reason:20} | {status}")
        
        return True

