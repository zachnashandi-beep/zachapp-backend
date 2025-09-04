from PyQt6 import QtWidgets, uic, QtCore
import os

# Import session management
try:
    from session_manager import session_manager, validate_session
except ImportError:
    session_manager = None


class WelcomeWindow(QtWidgets.QMainWindow):
    """Welcome window that loads welcome.ui and manages focus/animations properly."""
    logoutRequested = QtCore.pyqtSignal()

    def __init__(self, username: str):
        print(f"DEBUG: Initializing WelcomeWindow for {username}")
        super().__init__(None)  # No parent = independent window

        # Load UI with fallback
        try:
            ui_path = os.path.join(os.path.dirname(__file__), "welcome.ui")
            uic.loadUi(ui_path, self)
            # Set exact size from Designer
            self.resize(991, 621)
        except Exception as e:
            print(f"DEBUG: Could not load welcome.ui ({e}), using fallback window")
            self._create_fallback_window(username)
            self.resize(991, 621)  # Also set size for fallback
            return

        # Set proper window flags
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint
            | QtCore.Qt.WindowType.WindowCloseButtonHint
        )

        # Store widgets and username
        self.username = username
        self.welcome_label = self.findChild(QtWidgets.QLabel, "welcomeText")
        self.sub_message = self.findChild(QtWidgets.QLabel, "submessage")
        
        # Session management
        self.session_token = None
        if session_manager:
            session_info = session_manager.get_session_info(username)
            if session_info:
                self.session_token = session_info.get("token")

        # Store animation refs and state
        self._fade_anim = None
        self._sub_anim = None
        self._is_closing = False

        # Connect logout button if it exists
        self.logout_button = self.findChild(QtWidgets.QPushButton, "logoutButton")
        if self.logout_button:
            self.logout_button.clicked.connect(self._handle_logout)
        
        # Connect other buttons for session refresh
        self._connect_session_refresh_buttons()

        # Initial setup
        if self.welcome_label:
            self.welcome_label.setText("")  # start empty for typing effect
        if self.sub_message:
            self.sub_message.setText("")
            self.sub_message.setVisible(False)  # hide until typing done

        print("DEBUG: WelcomeWindow initialization complete")

    def _create_fallback_window(self, username: str):
        """Create basic window if welcome.ui fails to load"""
        self.setWindowTitle("Welcome")
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        self.welcome_label = QtWidgets.QLabel(f"Welcome, {username}!")
        self.sub_message = QtWidgets.QLabel("")
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logoutRequested.emit)

        layout.addWidget(self.welcome_label)
        layout.addWidget(self.sub_message)
        layout.addWidget(self.logout_btn)
        layout.addStretch()

    def _start_typing_animation(self):
        """Start typewriter effect for welcome text"""
        if not self.welcome_label:
            return

        self.full_text = f"Welcome, {self.username}!"
        self.current_pos = 0
        self.show_cursor = True

        # Create and store timers
        self._type_timer = QtCore.QTimer(self)
        self._cursor_timer = QtCore.QTimer(self)

        def type_char():
            if self.current_pos < len(self.full_text):
                self.current_pos += 1
                text = self.full_text[:self.current_pos]
                if self.show_cursor:
                    text += "█"  # solid block cursor
                self.welcome_label.setText(text)
            else:
                self._type_timer.stop()
                self._cursor_timer.stop()
                self.welcome_label.setText(self.full_text)
                self._start_submessage_fade()

        def blink_cursor():
            if self.current_pos < len(self.full_text):
                self.show_cursor = not self.show_cursor
                text = self.full_text[:self.current_pos]
                if self.show_cursor:
                    text += "█"
                self.welcome_label.setText(text)

        # Calculate timing for 4 second total duration
        char_interval = 4000 // len(self.full_text)
        self._type_timer.timeout.connect(type_char)
        self._type_timer.start(char_interval)

        self._cursor_timer.timeout.connect(blink_cursor)
        self._cursor_timer.start(500)  # cursor blinks twice per second

    def _start_submessage_fade(self):
        """Fade in the submessage after typing finishes"""
        if not self.sub_message:
            return

        self.sub_message.setText("You are logged in")
        self.sub_message.setVisible(True)
        self.sub_message.setStyleSheet("color: rgb(0, 0, 0, 0);")  # start transparent

        self._sub_anim = QtCore.QPropertyAnimation(self.sub_message, b"styleSheet", self)
        self._sub_anim.setDuration(1000)  # 1 second fade
        self._sub_anim.setStartValue("color: rgba(0, 0, 0, 0);")
        self._sub_anim.setEndValue("color: rgba(0, 0, 0, 255);")
        self._sub_anim.start()

    def fade_in(self, duration=400):
        """Window fade-in with proper focus"""
        print("DEBUG: Starting fade_in animation")
        # Show and focus window BEFORE animation
        self.show()
        self.raise_()
        self.activateWindow()

        # Start at 0 opacity
        self.setWindowOpacity(0.0)

        # Create and store animation
        self._fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(duration)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.finished.connect(self._start_typing_animation)
        self._fade_anim.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        print("DEBUG: Fade animation started")

    def _on_fade_complete(self):
        """Ensure window is focused after fade"""
        self.raise_()
        self.activateWindow()

    def _handle_logout(self):
        """Initiate logout if not already closing"""
        if not self._is_closing:
            self._is_closing = True
            self.logoutRequested.emit()
            self.close()

    def closeEvent(self, event):
        """Handle window close with safe animation cleanup"""
        print("DEBUG: WelcomeWindow closeEvent")

        # Prevent recursive closeEvent
        if self._is_closing:
            event.accept()
            return

        self._is_closing = True

        # Safe animation cleanup
        if hasattr(self, "_fade_anim") and self._fade_anim is not None:
            try:
                self._fade_anim.stop()
                self._fade_anim = None
            except RuntimeError:
                pass

        if hasattr(self, "_sub_anim") and self._sub_anim is not None:
            try:
                self._sub_anim.stop()
                self._sub_anim = None
            except RuntimeError:
                pass

        # Emit logout only if not triggered by button
        if not event.spontaneous():
            self.logoutRequested.emit()

        event.accept()
    
    def _connect_session_refresh_buttons(self):
        """Connect buttons to session refresh functionality"""
        if not session_manager or not self.session_token:
            return
        
        # Find common buttons that should refresh session
        buttons_to_connect = [
            "profileButton", "settingsButton", "homeButton", 
            "dashboardButton", "accountButton", "menuButton"
        ]
        
        for button_name in buttons_to_connect:
            button = self.findChild(QtWidgets.QPushButton, button_name)
            if button:
                # Connect to session refresh
                button.clicked.connect(self._refresh_session)
                print(f"DEBUG: Connected {button_name} to session refresh")
    
    def _refresh_session(self):
        """Refresh the user's session on interaction"""
        if not session_manager or not self.session_token:
            return
        
        try:
            if validate_session(self.username, self.session_token, 3600):
                print(f"DEBUG: Session refreshed for {self.username}")
            else:
                print(f"DEBUG: Session validation failed for {self.username}")
                # Session is invalid, could trigger re-login
                self._handle_session_expired()
        except Exception as e:
            print(f"Warning: Failed to refresh session: {e}")
    
    def _handle_session_expired(self):
        """Handle expired session"""
        print(f"DEBUG: Session expired for {self.username}")
        # Could show a dialog or automatically logout
        # For now, just log the event
        pass
    
    def set_session_token(self, token: str):
        """Set the session token for this window"""
        self.session_token = token
        print(f"DEBUG: Set session token for {self.username}")
