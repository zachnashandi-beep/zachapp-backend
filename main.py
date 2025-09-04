import sys, time, os, json, hashlib, re, datetime
from typing import Tuple
from PyQt6 import QtWidgets, uic, QtCore, QtGui

# Import session management
try:
    from session_manager import session_manager, create_session, validate_session, end_session, save_remember_me, clear_remember_me, auto_login_from_remember
except ImportError:
    print("Warning: session_manager not found, session features disabled")
    session_manager = None

# Import email verification
try:
    from email_verification import verification_manager, is_verified, verify_email
    from verification_popup import show_verification_popup, get_user_email
except ImportError:
    print("Warning: email_verification not found, email verification disabled")
    verification_manager = None

# Import password reset functionality
try:
    from forgot_password_dialog import show_forgot_password_dialog
    from reset_password_dialog import show_reset_password_dialog
except ImportError:
    print("Warning: password reset modules not found, forgot password disabled")
    show_forgot_password_dialog = None
    show_reset_password_dialog = None

# Import hybrid user manager for case-insensitive login
try:
    from hybrid_user_manager import user_manager, validate_user_credentials_case_insensitive
except ImportError:
    print("Warning: hybrid_user_manager not found, using fallback login system")
    user_manager = None

# Import database signal monitor with async support
try:
    from database_signal_monitor import DatabaseSignalButton, init_async_db_monitor
except ImportError:
    print("Warning: database_signal_monitor not found, database signal monitoring disabled")
    DatabaseSignalButton = None
    init_async_db_monitor = None

# Import the real Welcome window (do NOT define another WelcomeWindow here)
# Ensure welcome.py is in the same directory as main.py, or adjust the import path if needed.
try:
    from welcome import WelcomeWindow
except ModuleNotFoundError:
    raise ImportError("Could not import 'WelcomeWindow' from 'welcome.py'. Make sure 'welcome.py' exists in the same directory as 'main.py'.")

# Import SignupDialog from signup.py
try:
    from signup import SignupDialog
except ModuleNotFoundError:
    raise ImportError("Could not import 'SignupDialog' from 'signup.py'. Make sure 'signup.py' exists in the same directory as 'main.py'.")


def ui_path(name: str) -> str:
    """Resolve a .ui path relative to this file, with a safe fallback."""
    try:
        base = os.path.dirname(__file__)
        path = os.path.join(base, name)
        return path if os.path.exists(path) else name
    except NameError:
        return name

# ---- App & Login UI ----
app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(lambda: print("DEBUG: Application is quitting"))
window = uic.loadUi(ui_path("Login.ui"))
window.setWindowTitle("Login")

# Disable login button initially
if hasattr(window, "Login") and isinstance(window.Login, QtWidgets.QPushButton):
    window.Login.setEnabled(False)

# Password field: always masked by default
if hasattr(window, "Password"):
    window.Password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

# Database signal button setup - moved to function
def initialize_db_monitor():
    """Initialize database monitoring in background thread."""
    if not hasattr(window, "dbstrength") or not DatabaseSignalButton:
        print("⚠️ Database signal button not found or monitor not available")
        return

    try:
        # Create button without initial connection test to avoid blocking startup
        db_button = DatabaseSignalButton(window, 30, skip_initial_test=True)
        db_button.setGeometry(window.dbstrength.geometry())
        db_button.setParent(window)
        db_button.show()
        window.dbstrength.hide()

        # Start async monitoring in background thread
        if init_async_db_monitor:
            init_async_db_monitor(db_button, 1000)  # 1 second interval
            print("✅ Database signal monitoring initialized in background")
        else:
            print("⚠️ init_async_db_monitor not available")
    except Exception as e:
        print(f"⚠️ Failed to setup database signal button: {e}")
        # Ensure the original button is hidden even if setup fails
        if hasattr(window, "dbstrength"):
            window.dbstrength.hide()

# TogglePassword button: make transparent and clickable, toggles echo mode
if hasattr(window, "TogglePassword") and hasattr(window, "Password"):
    btn = window.TogglePassword
    if isinstance(btn, (QtWidgets.QToolButton, QtWidgets.QPushButton)):
        try:
            btn.setCheckable(True)
        except Exception:
            pass
        try:
            btn.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        except Exception:
            pass
        # Keep background fully transparent
        try:
            btn.setStyleSheet(
                "QToolButton{background:transparent;border:none;padding:0;}"
                "QToolButton:pressed{background:transparent;}"
                "QPushButton{background:transparent;border:none;padding:0;}"
                "QPushButton:pressed{background:transparent;}"
            )
        except Exception:
            pass

        # Load custom icons
        EYE_OPEN_PATH = ui_path("emoji/eye.png")
        EYE_CLOSED_PATH = ui_path("emoji/hidden.png")
        eye_open_icon = QtGui.QIcon(EYE_OPEN_PATH)
        eye_closed_icon = QtGui.QIcon(EYE_CLOSED_PATH)

        def _update_toggle_ui(checked: bool):
            if checked:
                window.Password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
                # Visible -> open eye icon
                if not eye_open_icon.isNull():
                    btn.setIcon(eye_open_icon)
                    btn.setText("")
                    btn.setIconSize(QtCore.QSize(30, 30))
                else:
                    btn.setText("👁")
            else:
                window.Password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
                # Hidden -> closed eye icon
                if not eye_closed_icon.isNull():
                    btn.setIcon(eye_closed_icon)
                    btn.setText("")
                    btn.setIconSize(QtCore.QSize(30, 30))
                else:
                    btn.setText("🙈")

        # Initialize state
        if hasattr(btn, "toggled"):
            btn.toggled.connect(_update_toggle_ui)
        # Ensure default is hidden (unchecked)
        try:
            btn.setChecked(False)
        except Exception:
            pass
        _update_toggle_ui(False)

# Login button: prevent "Enter" from auto-clicking it when focus is elsewhere
if hasattr(window, "Login") and isinstance(window.Login, QtWidgets.QPushButton):
    window.Login.setAutoDefault(False)
    window.Login.setDefault(False)

# Forgot password hyperlink
if hasattr(window, "ForgotPassword") and isinstance(window.ForgotPassword, QtWidgets.QLabel):
    window.ForgotPassword.setText('<a href="#">Forgot password?</a>')
    window.ForgotPassword.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
    window.ForgotPassword.setOpenExternalLinks(False)
    window.ForgotPassword.linkActivated.connect(
        lambda _: _handle_forgot_password(window)
    )

# ---- Lockout / attempts ----
FAILED_ATTEMPTS_LIMIT = 3
FAILED_ATTEMPTS_FILE = "failed_attempts.txt"
LOCKOUT_FILE = "lockout_state.txt"
LOCKOUT_DURATION_FILE = "lockout_duration.txt"
DEFAULT_LOCKOUT_DURATION = 10  # seconds
countdown_timer = QtCore.QTimer()

# Remember-me
REMEMBER_FILE = "remember.json"


def load_users() -> dict:
    """
    Load users.json and return {username: {"password": "<hash-or-plain>", "email": "<email>"}}.
    Handles both old structure and new hybrid structure.
    """
    path = ui_path("users.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        result = {}
        
        # Check if it's the new hybrid structure (direct username keys)
        if isinstance(data, dict) and data and not any(key == "users" for key in data.keys()):
            # New hybrid structure: {username: {username, email, password}}
            for uname, val in data.items():
                if isinstance(val, dict):
                    pw = val.get("password", "") or ""
                    em = val.get("email", "") or ""
                    result[uname] = {"password": pw, "email": em}
        else:
            # Old structure: {users: {username: {password, email}}}
            raw = data.get("users", {}) if isinstance(data, dict) else {}
            for uname, val in raw.items():
                if isinstance(val, str):
                    result[uname] = {"password": val, "email": ""}
                elif isinstance(val, dict):
                    pw = val.get("password", "") or ""
                    em = val.get("email", "") or ""
                    result[uname] = {"password": pw, "email": em}
        
        return result
    except Exception as e:
        print("Warning: failed to load users.json:", e)
        return {}


def save_user(username: str, password_hash: str, email: str) -> bool:
    """Add/update a user in users.json; returns True on success."""
    path = ui_path("users.json")
    data = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
    users_obj = data.get("users", {}) if isinstance(data, dict) else {}
    users_obj[username] = {"password": password_hash, "email": email}
    data["users"] = users_obj
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print("Error saving users.json:", e)
        return False


def get_lockout_duration() -> int:
    if os.path.exists(LOCKOUT_DURATION_FILE):
        try:
            return int(open(LOCKOUT_DURATION_FILE).read())
        except Exception:
            pass
    return DEFAULT_LOCKOUT_DURATION


def set_lockout_duration(duration: int) -> None:
    with open(LOCKOUT_DURATION_FILE, "w") as f:
        f.write(str(duration))


def reset_lockout_duration() -> None:
    set_lockout_duration(DEFAULT_LOCKOUT_DURATION)


def save_lockout() -> None:
    with open(LOCKOUT_FILE, "w") as f:
        f.write(str(int(time.time())))


def clear_lockout() -> None:
    if os.path.exists(LOCKOUT_FILE):
        os.remove(LOCKOUT_FILE)


def is_locked_out():
    if not os.path.exists(LOCKOUT_FILE):
        return False
    with open(LOCKOUT_FILE, "r") as f:
        lock_time = int(f.read())
    duration = get_lockout_duration()
    elapsed = time.time() - lock_time
    if elapsed < duration:
        return duration - elapsed
    clear_lockout()
    return False


def format_time(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds//60}m {seconds%60}s" if seconds >= 60 else f"{seconds}s"


def unlock_login():
    for name in ("Login", "Username", "Password"):
        if hasattr(window, name):
            getattr(window, name).setEnabled(True)
    if hasattr(window, "Login"):
        window.Login.setText("Login")
    window.setWindowTitle("Login")
    clear_lockout()
    countdown_timer.stop()
    set_lockout_duration(get_lockout_duration() * 2)  # backoff


def update_countdown():
    remaining = is_locked_out()
    if remaining and hasattr(window, "Login") and not window.Login.isEnabled():
        time_str = format_time(remaining)
        window.Login.setText(f"Locked ({time_str} left)")
        window.setWindowTitle(f"Login (Locked: {time_str} left)")


def load_failed_attempts() -> int:
    if os.path.exists(FAILED_ATTEMPTS_FILE):
        try:
            return int(open(FAILED_ATTEMPTS_FILE).read())
        except Exception:
            return 0
    return 0


def save_failed_attempts(value: int) -> None:
    with open(FAILED_ATTEMPTS_FILE, "w") as f:
        f.write(str(value))


def write_login_history(username: str, action: str) -> None:
    path = ui_path("login_history.txt")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} - User: {username} - {action}\n"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("Warning: could not write login history:", e)


def save_remembered_login(username: str, email: str | None = None):
    try:
        data = {"username": username, "email": email} if email else {"username": username}
        with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print("Warning: couldn't save remembered login:", e)


def load_remembered_login() -> Tuple[str, str]:
    try:
        if os.path.exists(REMEMBER_FILE):
            with open(REMEMBER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("username", ""), data.get("email", "")
    except Exception as e:
        print("Warning: couldn't load remembered login:", e)
    return "", ""


def clear_remembered_login():
    try:
        if os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)
    except Exception as e:
        print("Warning: couldn't clear remembered login:", e)


failed_attempts = load_failed_attempts()
users = load_users()
welcome_win = None  # keep a reference so it isn't GC'd


def _password_matches(stored: str, typed: str) -> bool:
    """Accept legacy plain or sha256-hash matches (non-breaking)."""
    typed_hash = hashlib.sha256(typed.encode("utf-8")).hexdigest()
    return stored == typed or stored == typed_hash


# Add new constant for per-user tracking
USER_ATTEMPTS_FILE = "user_attempts.json"

def load_user_attempts() -> dict:
    """Load per-user failed attempts."""
    if os.path.exists(USER_ATTEMPTS_FILE):
        try:
            with open(USER_ATTEMPTS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_attempts(attempts: dict) -> None:
    """Save per-user failed attempts."""
    with open(USER_ATTEMPTS_FILE, "w") as f:
        json.dump(attempts, f)

def get_user_attempts(username: str) -> int:
    """Get failed attempts for specific user."""
    attempts = load_user_attempts()
    return attempts.get(username, 0)

def increment_user_attempts(username: str) -> int:
    """Increment and return attempts for user."""
    attempts = load_user_attempts()
    attempts[username] = attempts.get(username, 0) + 1
    save_user_attempts(attempts)
    return attempts[username]

def reset_user_attempts(username: str) -> None:
    """Reset attempts for specific user."""
    attempts = load_user_attempts()
    if username in attempts:
        del attempts[username]
        save_user_attempts(attempts)


def handle_login(triggered_by_button=False, triggered_by_password_enter=False):
    global failed_attempts, welcome_win, users
    print(f"DEBUG: handle_login called (button={triggered_by_button}, enter={triggered_by_password_enter})")

    username = window.Username.text() if hasattr(window, "Username") else ""
    password = window.Password.text() if hasattr(window, "Password") else ""

    if not username or not password:
        if triggered_by_button or triggered_by_password_enter:
            QtWidgets.QMessageBox.warning(window, "Input Error", "Please fill in all fields.")
        return

    # First check if username exists
    username_exists = False
    actual_username = username
    
    if user_manager:
        user_data = user_manager.get_user_case_insensitive(username)
        if user_data:
            username_exists = True
            actual_username = user_data["username"]
    else:
        if username in users:
            username_exists = True
            actual_username = username

    if not username_exists:
        if triggered_by_button or triggered_by_password_enter:
            QtWidgets.QMessageBox.critical(window, "Login Failed", 
                "This account does not exist. Please check your username or sign up for a new account.")
        return

    # For existing users, check if they're locked out
    user_attempts = get_user_attempts(actual_username)
    if user_attempts >= FAILED_ATTEMPTS_LIMIT:
        lockout_remaining = is_locked_out()
        if lockout_remaining:
            if triggered_by_button or triggered_by_password_enter:
                # Instead of showing message, disable UI
                for name in ("Login", "Username", "Password"):
                    if hasattr(window, name):
                        getattr(window, name).setEnabled(False)
                if hasattr(window, "Login"):
                    window.Login.setText(f"Locked ({format_time(lockout_remaining)} left)")
                window.setWindowTitle(f"Login (Locked: {format_time(lockout_remaining)} left)")
                countdown_timer.start(1000)
            return

    # Now validate password for existing user
    login_valid = False
    if user_manager:
        login_valid, returned_username = validate_user_credentials_case_insensitive(username, password)
        if login_valid:
            actual_username = returned_username
    else:
        login_valid = _password_matches(users[actual_username]["password"], password)

    if not login_valid:
        attempts_left = FAILED_ATTEMPTS_LIMIT - increment_user_attempts(actual_username)
        
        if triggered_by_button or triggered_by_password_enter:
            if attempts_left <= 0:
                # Show lockout message
                QtWidgets.QMessageBox.critical(window, "Locked Out",
                                             "Too many failed attempts. Please wait before trying again.")
                # Disable fields and start countdown
                for name in ("Login", "Username", "Password"):
                    if hasattr(window, name):
                        getattr(window, name).setEnabled(False)
                duration = get_lockout_duration()
                if hasattr(window, "Login"):
                    window.Login.setText(f"Locked ({format_time(duration)} left)")
                window.setWindowTitle(f"Login (Locked: {format_time(duration)} left)")
                save_lockout()
                QtCore.QTimer.singleShot(duration * 1000, lambda: (
                    unlock_login()
                ))
                countdown_timer.start(1000)
            else:
                # Just show attempts remaining
                QtWidgets.QMessageBox.critical(
                    window, 
                    "Login Failed", 
                    f"Incorrect username or password.\nAttempts left: {attempts_left}"
                )
        return

    # Reset attempts and continue with successful login
    reset_user_attempts(actual_username)
    
    # Check email verification (use actual_username for consistency)
    if verification_manager and not is_verified(actual_username):
        print(f"DEBUG: User {actual_username} is not verified")
        
        # Get user's email
        user_email = get_user_email(actual_username)
        if not user_email:
            QtWidgets.QMessageBox.critical(
                window, 
                "Email Not Found", 
                f"No email address found for user '{actual_username}'.\n\n"
                f"Please contact support for assistance."
            )
            return
        
        # Show verification popup
        verification_sent = show_verification_popup(window, actual_username, user_email)
        
        if verification_sent:
            print(f"DEBUG: Verification email sent to {user_email}")
            # Don't proceed with login - user needs to verify first
            return
        else:
            print(f"DEBUG: User declined to send verification email")
            # Don't proceed with login - user needs to verify first
            return
    # Remember Me
    if hasattr(window, "RememberMe") and window.RememberMe.isChecked():
        # Get user email for remember me
        if user_manager:
            user_data = user_manager.get_user_case_insensitive(username)
            user_email = user_data.get("email") if user_data else None
        else:
            user_email = users[username].get("email") if username in users else None
        save_remembered_login(actual_username, user_email)
    else:
        clear_remembered_login()

    # Reset attempts / lockout
    failed_attempts = 0
    save_failed_attempts(failed_attempts)
    clear_lockout()
    reset_lockout_duration()

    write_login_history(actual_username, "Logged in")

    # Create session for the user
    if session_manager:
        try:
            session_token = create_session(actual_username, 3600)  # 1 hour session
            print(f"DEBUG: Created session for {actual_username}")
            
            # Save remember me if checked
            if hasattr(window, "RememberMe") and window.RememberMe.isChecked():
                save_remember_me(actual_username, session_token)
                print(f"DEBUG: Saved remember me for {actual_username}")
            else:
                clear_remember_me()
                print(f"DEBUG: Cleared remember me data")
        except Exception as e:
            print(f"Warning: Failed to create session: {e}")

    print("DEBUG: About to hide login window")
    window.hide()
    
    print("DEBUG: Creating WelcomeWindow")
    welcome_win = WelcomeWindow(actual_username)
    welcome_win.resize(800, 600)
    
    # Set session token if available
    if session_manager and 'session_token' in locals():
        welcome_win.set_session_token(session_token)

    def _on_logout():
        global welcome_win
        print("DEBUG: _on_logout called")
        
        # Prevent multiple calls
        if not welcome_win:
            return
        
        # End session
        if session_manager:
            try:
                end_session(actual_username)
                print(f"DEBUG: Ended session for {actual_username}")
            except Exception as e:
                print(f"Warning: Failed to end session: {e}")
            
        write_login_history(actual_username, "Logged out")
        
        # Close welcome window first
        temp_win = welcome_win
        welcome_win = None  # Clear reference before closing
        temp_win.close()
        
        # Clear fields based on Remember Me
        window.Password.clear()
        if not (hasattr(window, "RememberMe") and window.RememberMe.isChecked()):
            window.Username.clear()
        
        # Re-enable login controls
        for name in ("Login", "Username", "Password"):
            if hasattr(window, name):
                widget = getattr(window, name)
                if widget:
                    widget.setEnabled(True)
        
        # Restore login window
        window.show()
        QtCore.QTimer.singleShot(0, lambda: (window.raise_(), window.activateWindow()))
        print("DEBUG: Login window restored")

    # Create and show welcome window
    welcome_win.logoutRequested.connect(_on_logout)
    welcome_win.fade_in(duration=400)

    # Hide login window after welcome window is ready
    window.hide()
    return

def _handle_forgot_password(parent):
    """Handle forgot password request"""
    if show_forgot_password_dialog is None:
        QtWidgets.QMessageBox.critical(parent, "Feature Unavailable", 
                                     "Password reset feature is not available.")
        return
    
    # Show forgot password dialog
    result = show_forgot_password_dialog(parent)
    
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        # Optionally show reset password dialog if user wants to reset immediately
        # This could be triggered by a button in the forgot password dialog
        pass

# Add validation to enable/disable login button
def _validate_login_fields():
    if not all(hasattr(window, name) for name in ("Login", "Username", "Password")):
        return
    has_content = bool(
        window.Username.text().strip() and 
        window.Password.text().strip()
    )
    window.Login.setEnabled(has_content)

# Connect text changed signals
if hasattr(window, "Username"):
    window.Username.textChanged.connect(_validate_login_fields)
if hasattr(window, "Password"):
    window.Password.textChanged.connect(_validate_login_fields)

# ---- Signup dialog ----
# Use SignupDialog from signup.py instead of re-implementing validation here


def open_signup_dialog():
    dialog = SignupDialog(window)
    
    def handle_signup(username: str, password_hash: str, email: str):
        global users
        
        # Use hybrid user manager for signup
        if user_manager:
            # Check if user already exists (case-insensitive)
            existing_user = user_manager.get_user_case_insensitive(username)
            if existing_user:
                QtWidgets.QMessageBox.warning(
                    dialog, 
                    "Error", 
                    "Username already exists."
                )
                return
            
            # Save user using hybrid system
            if user_manager.save_user(username, email, password_hash):
                users = load_users()  # Reload for compatibility
                QtWidgets.QMessageBox.information(
                    dialog,
                    "Success",
                    "Account created successfully!"
                )
                dialog.accept()
            else:
                QtWidgets.QMessageBox.warning(
                    dialog,
                    "Error",
                    "Failed to save user."
                )
        else:
            # Fallback to old system
            if username in users:
                QtWidgets.QMessageBox.warning(
                    dialog, 
                    "Error", 
                    "Username already exists."
                )
                return
                
            if save_user(username, password_hash, email):
                users = load_users()
                QtWidgets.QMessageBox.information(
                    dialog,
                    "Success",
                    "Account created successfully!"
                )
                dialog.accept()
            else:
                QtWidgets.QMessageBox.warning(
                    dialog,
                    "Error",
                    "Failed to save user."
                )
            
    dialog.signupCompleted.connect(handle_signup)
    dialog.exec()

# ---- Signals ----
if hasattr(window, "Login"):
    window.Login.clicked.connect(lambda: handle_login(triggered_by_button=True))

if hasattr(window, "Username") and hasattr(window, "Password"):
    window.Username.returnPressed.connect(lambda: window.Password.setFocus())
    window.Password.returnPressed.connect(
        lambda: handle_login(triggered_by_password_enter=True)
        if window.Username.text() and window.Password.text()
        else None
    )

countdown_timer.timeout.connect(update_countdown)

# Hook "Sign Up" link
if hasattr(window, "signupLink") and isinstance(window.signupLink, QtWidgets.QLabel):
    window.signupLink.setText('<a href="#">Don\'t have an account? Sign up</a>')
    window.signupLink.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
    window.signupLink.setOpenExternalLinks(False)
    window.signupLink.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
    window.signupLink.linkActivated.connect(open_signup_dialog)

# Verification is now handled automatically during login - no separate button needed

# ---- Lockout state on startup ----
remaining = is_locked_out()
if remaining:
    for name in ("Login", "Username", "Password"):
        if hasattr(window, name):
            getattr(window, name).setEnabled(False)
    if hasattr(window, "Login"):
        window.Login.setText(f"Locked ({format_time(remaining)} left)")
    window.setWindowTitle(f"Login (Locked: {format_time(remaining)} left)")
    QtCore.QTimer.singleShot(int(remaining) * 1000, unlock_login)
    countdown_timer.start(1000)
else:
    reset_lockout_duration()

# ---- Auto-login from session ----
auto_login_user = None
if session_manager:
    try:
        auto_login_user = auto_login_from_remember()
        if auto_login_user:
            print(f"DEBUG: Auto-login successful for {auto_login_user}")
            # Skip showing login window, go directly to welcome
            welcome_win = WelcomeWindow(auto_login_user)
            welcome_win.resize(800, 600)
            
            # Set session token for auto-login
            if session_manager:
                session_info = session_manager.get_session_info(auto_login_user)
                if session_info:
                    welcome_win.set_session_token(session_info.get("token"))
            
            def _on_auto_logout():
                global welcome_win
                print("DEBUG: _on_auto_logout called")
                
                if not welcome_win:
                    return
                
                # End session
                if session_manager:
                    try:
                        end_session(auto_login_user)
                        print(f"DEBUG: Ended auto-login session for {auto_login_user}")
                    except Exception as e:
                        print(f"Warning: Failed to end auto-login session: {e}")
                
                write_login_history(auto_login_user, "Logged out (auto-login)")
                
                # Close welcome window
                temp_win = welcome_win
                welcome_win = None
                temp_win.close()
                
                # Show login window
                window.show()
                QtCore.QTimer.singleShot(0, lambda: (window.raise_(), window.activateWindow()))
                print("DEBUG: Returned to login window")
            
            welcome_win.logoutRequested.connect(_on_auto_logout)
            welcome_win.fade_in(duration=400)
            
            # Don't show login window
            sys.exit(app.exec())
    except Exception as e:
        print(f"Warning: Auto-login failed: {e}")

# ---- Remembered login (fallback) ----
if not auto_login_user:
    remembered_user, remembered_email = load_remembered_login()
    if remembered_user and hasattr(window, "Username"):
        window.Username.setText(remembered_user)
        if hasattr(window, "Email"):
            window.Email.setText(remembered_email)

# Initialize database monitoring in background after UI is ready
QtCore.QTimer.singleShot(100, initialize_db_monitor)  # Small delay to ensure UI is ready

# ---- Run ----
window.show()
sys.exit(app.exec())
