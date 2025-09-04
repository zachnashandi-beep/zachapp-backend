import sys, time, os, json, hashlib, re, datetime
from typing import Tuple
from PyQt6 import QtWidgets, uic, QtCore, QtGui

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

# Password field: always masked by default
if hasattr(window, "Password"):
    window.Password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

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
                    btn.setIconSize(QtCore.QSize(25, 25))
                else:
                    btn.setText("👁")
            else:
                window.Password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
                # Hidden -> closed eye icon
                if not eye_closed_icon.isNull():
                    btn.setIcon(eye_closed_icon)
                    btn.setText("")
                    btn.setIconSize(QtCore.QSize(25, 25))
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
        lambda _:
            QtWidgets.QMessageBox.information(window, "Forgot Password",
                                              "Password reset panel would open here.")
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
    Accept legacy plain passwords too (no breaking change).
    """
    path = ui_path("users.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw = data.get("users", {}) if isinstance(data, dict) else {}
        result = {}
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


def handle_login(triggered_by_button=False, triggered_by_password_enter=False):
    global failed_attempts, welcome_win, users
    print(f"DEBUG: handle_login called (button={triggered_by_button}, enter={triggered_by_password_enter})")

    username = window.Username.text() if hasattr(window, "Username") else ""
    password = window.Password.text() if hasattr(window, "Password") else ""
    print(f"DEBUG: Attempting login for user: {username}")

    if not username or not password:
        if triggered_by_button or triggered_by_password_enter:
            QtWidgets.QMessageBox.warning(window, "Input Error", "Please fill in all fields.")
        return

    # Validate
    if username in users and _password_matches(users[username]["password"], password):
        print("DEBUG: Login validation successful")
        # Remember Me
        if hasattr(window, "RememberMe") and window.RememberMe.isChecked():
            save_remembered_login(username, users[username].get("email"))
        else:
            clear_remembered_login()

        # Reset attempts / lockout
        failed_attempts = 0
        save_failed_attempts(failed_attempts)
        clear_lockout()
        reset_lockout_duration()

        write_login_history(username, "Logged in")

        print("DEBUG: About to hide login window")
        window.hide()
        
        print("DEBUG: Creating WelcomeWindow")
        welcome_win = WelcomeWindow(username)
        welcome_win.resize(800, 600)

        def _on_logout():
            global welcome_win
            print("DEBUG: _on_logout called")
            
            # Prevent multiple calls
            if not welcome_win:
                return
                
            write_login_history(username, "Logged out")
            
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

    # Invalid login
    failed_attempts += 1
    save_failed_attempts(failed_attempts)
    attempts_left = FAILED_ATTEMPTS_LIMIT - failed_attempts
    if failed_attempts >= FAILED_ATTEMPTS_LIMIT:
        QtWidgets.QMessageBox.critical(window, "Locked Out",
                                       "Too many failed attempts. Please wait before trying again.")
        for name in ("Login", "Username", "Password"):
            if hasattr(window, name):
                getattr(window, name).setEnabled(False)
        duration = get_lockout_duration()
        time_str = format_time(duration)
        if hasattr(window, "Login"):
            window.Login.setText(f"Locked ({time_str} left)")
        window.setWindowTitle(f"Login (Locked: {time_str} left)")
        save_lockout()
        QtCore.QTimer.singleShot(duration * 1000, unlock_login)
        countdown_timer.start(1000)
    else:
        QtWidgets.QMessageBox.critical(window, "Login Failed",
                                       f"Incorrect username or password.\nAttempts left: {attempts_left}")

# ---- Signup dialog ----
# Use SignupDialog from signup.py instead of re-implementing validation here


def open_signup_dialog():
    dialog = SignupDialog(window)
    
    def handle_signup(username: str, password_hash: str, email: str):
        global users
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

# ---- Remembered login ----
remembered_user, remembered_email = load_remembered_login()
if remembered_user and hasattr(window, "Username"):
    window.Username.setText(remembered_user)
    if hasattr(window, "Email"):
        window.Email.setText(remembered_email)

# ---- Run ----
window.show()
sys.exit(app.exec())
