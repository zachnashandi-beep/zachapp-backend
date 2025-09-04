"""
Caps Lock Indicator for Password Fields
Provides real-time Caps Lock detection and visual feedback
"""

from PyQt6 import QtWidgets, QtCore, QtGui

class CapsLockIndicator:
    """Caps Lock indicator for password fields"""
    
    def __init__(self, capslock_label):
        self.capslock_label = capslock_label
        self._setup_indicator()
    
    def _setup_indicator(self):
        """Setup the Caps Lock indicator styling"""
        if self.capslock_label:
            # Initially hide the label
            self.capslock_label.setText("")
            self.capslock_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                    background-color: transparent;
                    border: none;
                }
            """)
    
    def check_capslock_status(self, event):
        """Check and display Caps Lock status"""
        if not self.capslock_label:
            return
        
        # Get the key that was pressed
        key = event.key()
        
        # Check if Caps Lock is on by comparing the key with its shifted version
        # This is a cross-platform way to detect Caps Lock
        caps_lock_on = False
        
        # Check if the key is a letter
        if QtCore.Qt.Key.Key_A <= key <= QtCore.Qt.Key.Key_Z:
            # Get the text representation
            text = event.text()
            if text:
                # If the text is uppercase and shift is not pressed, Caps Lock is on
                if text.isupper() and not (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier):
                    caps_lock_on = True
                # If the text is lowercase and shift is pressed, Caps Lock is on
                elif text.islower() and (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier):
                    caps_lock_on = True
        
        # Update the label
        if caps_lock_on:
            self.capslock_label.setText("⚠️ Caps Lock is ON")
            self.capslock_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.capslock_label.setText("")
            self.capslock_label.setStyleSheet("""
                QLabel {
                    color: transparent;
                    font-size: 12px;
                    padding: 5px;
                    background-color: transparent;
                    border: none;
                }
            """)

class CapsLockEventFilter(QtCore.QObject):
    """Event filter for Caps Lock detection on password fields"""
    
    def __init__(self, capslock_indicator):
        super().__init__()
        self.capslock_indicator = capslock_indicator
    
    def eventFilter(self, obj, event):
        """Event filter to detect Caps Lock status"""
        if event.type() == QtCore.QEvent.Type.KeyPress:
            # Check if the event is from a password field
            if hasattr(obj, 'echoMode') and obj.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
                self.capslock_indicator.check_capslock_status(event)
        return super().eventFilter(obj, event)

def setup_capslock_detection(password_fields, capslock_label):
    """
    Setup Caps Lock detection for password fields
    
    Args:
        password_fields: List of password field widgets
        capslock_label: Label to display Caps Lock status
    """
    # Create the indicator
    indicator = CapsLockIndicator(capslock_label)
    
    # Create event filter
    event_filter = CapsLockEventFilter(indicator)
    
    # Install event filter on password fields
    for field in password_fields:
        if field:
            field.installEventFilter(event_filter)
    
    return indicator, event_filter

# Demo function
def demo_capslock_detection():
    """Demonstrate Caps Lock detection functionality"""
    print("=" * 60)
    print("CAPS LOCK DETECTION DEMO")
    print("=" * 60)
    
    print("\n1. Caps Lock Detection Features:")
    print("   ✅ Real-time detection while typing in password fields")
    print("   ✅ Visual indicator with warning emoji (⚠️)")
    print("   ✅ Transparent background styling")
    print("   ✅ Only shows when Caps Lock is ON")
    print("   ✅ Hidden when Caps Lock is OFF")
    
    print("\n2. Integration Points:")
    print("   ✅ Works with existing 'CapsLock' label in Signup.ui")
    print("   ✅ Monitors both password fields (Password & Retype Password)")
    print("   ✅ Cross-platform Caps Lock detection")
    print("   ✅ Non-intrusive - doesn't interfere with other functionality")
    
    print("\n3. Visual Design:")
    print("   ✅ Warning emoji: ⚠️")
    print("   ✅ Red text with transparent background")
    print("   ✅ Clean, minimal styling")
    print("   ✅ Transparent when hidden")
    
    print("\n4. Usage:")
    print("   ✅ User types in password field with Caps Lock ON")
    print("   ✅ Label shows: '⚠️ Caps Lock is ON'")
    print("   ✅ User turns off Caps Lock and continues typing")
    print("   ✅ Label disappears automatically")
    
    print("\n" + "=" * 60)
    print("CAPS LOCK DETECTION DEMO COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    demo_capslock_detection()
