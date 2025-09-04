#!/usr/bin/env python3
"""
Caps Lock Indicator Demo
Demonstrates the Caps Lock detection functionality in the signup form
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

class CapsLockDemoWindow(QtWidgets.QMainWindow):
    """Demo window to test Caps Lock functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caps Lock Indicator Demo")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add title
        title = QtWidgets.QLabel("Caps Lock Indicator Demo")
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
        <h3>Instructions:</h3>
        <ol>
            <li>Click "Open Signup Form" to open the signup dialog</li>
            <li>Click on either password field (Password or Retype Password)</li>
            <li>Turn Caps Lock ON and type some letters</li>
            <li>You should see "⚠️ Caps Lock is ON" appear</li>
            <li>Turn Caps Lock OFF and continue typing</li>
            <li>The indicator should disappear</li>
        </ol>
        
                 <h3>Features:</h3>
         <ul>
             <li>✅ Real-time Caps Lock detection</li>
             <li>✅ Visual warning with emoji (⚠️)</li>
             <li>✅ Transparent background styling</li>
             <li>✅ Only shows when Caps Lock is ON</li>
             <li>✅ Works on both password fields</li>
             <li>✅ Cross-platform detection</li>
         </ul>
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
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.open_button.clicked.connect(self.open_signup_form)
        layout.addWidget(self.open_button)
        
        # Add status label
        self.status_label = QtWidgets.QLabel("Ready to test Caps Lock detection")
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
                color: #e74c3c;
                padding: 10px;
                text-align: center;
            """)

def demo_capslock_functionality():
    """Demonstrate Caps Lock functionality"""
    print("=" * 70)
    print("CAPS LOCK INDICATOR DEMO")
    print("=" * 70)
    
    print("\n1. Features Implemented:")
    print("   ✅ Real-time Caps Lock detection")
    print("   ✅ Visual indicator with warning emoji (⚠️)")
    print("   ✅ Transparent background styling")
    print("   ✅ Only shows when Caps Lock is ON")
    print("   ✅ Hidden when Caps Lock is OFF")
    print("   ✅ Works on both password fields")
    print("   ✅ Cross-platform detection")
    
    print("\n2. Integration:")
    print("   ✅ Uses existing 'CapsLock' label in Signup.ui")
    print("   ✅ Modular implementation for easy maintenance")
    print("   ✅ Non-intrusive - doesn't interfere with other functionality")
    print("   ✅ Event filter approach for efficient detection")
    
    print("\n3. Visual Design:")
    print("   ✅ Warning emoji: ⚠️")
    print("   ✅ Red text with transparent background")
    print("   ✅ Clean, minimal styling")
    print("   ✅ Transparent when hidden")
    print("   ✅ Consistent with existing UI styling")
    
    print("\n4. Technical Implementation:")
    print("   ✅ Cross-platform Caps Lock detection")
    print("   ✅ Event filter for efficient key monitoring")
    print("   ✅ Modular design for easy maintenance")
    print("   ✅ Proper error handling and fallbacks")
    
    print("\n" + "=" * 70)
    print("CAPS LOCK INDICATOR DEMO COMPLETE")
    print("=" * 70)

def main():
    """Main function to run the demo"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Show console demo
    demo_capslock_functionality()
    
    # Show GUI demo
    window = CapsLockDemoWindow()
    window.show()
    
    print("\n" + "=" * 70)
    print("GUI DEMO STARTED")
    print("=" * 70)
    print("Click 'Open Signup Form' to test the Caps Lock indicator!")
    print("=" * 70)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
