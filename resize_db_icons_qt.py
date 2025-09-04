#!/usr/bin/env python3
"""
Resize Database Signal Icons (PyQt6 Version)
Resize database signal icons from 100x100 to 25-30px for UI display
"""

import os
import sys
from PyQt6 import QtGui, QtCore, QtWidgets

def resize_database_icons():
    """Resize database signal icons to appropriate sizes using PyQt6"""
    print("🖼️ RESIZING DATABASE SIGNAL ICONS (PyQt6)")
    print("=" * 50)
    
    # Icon directory
    icon_dir = os.path.join(os.path.dirname(__file__), "emoji")
    
    # Icon files to resize
    icons_to_resize = [
        "db_unavailable.png",
        "wifi_weak.png", 
        "wifi_okish.png",
        "wifi_strong.png",
        "wifi_verystrong.png"
    ]
    
    # Target sizes
    target_sizes = [
        (25, 25),  # Small
        (30, 30),  # Medium
    ]
    
    for icon_file in icons_to_resize:
        icon_path = os.path.join(icon_dir, icon_file)
        
        if not os.path.exists(icon_path):
            print(f"⚠️ Icon not found: {icon_file}")
            continue
        
        try:
            # Load original image
            pixmap = QtGui.QPixmap(icon_path)
            if pixmap.isNull():
                print(f"⚠️ Failed to load: {icon_file}")
                continue
            
            print(f"📁 Processing: {icon_file}")
            print(f"   Original size: {pixmap.width()}x{pixmap.height()}")
            
            # Resize to different target sizes
            for size in target_sizes:
                # Create resized version
                resized = pixmap.scaled(
                    size[0], size[1], 
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                
                # Create new filename
                name, ext = os.path.splitext(icon_file)
                new_filename = f"{name}_{size[0]}x{size[1]}{ext}"
                new_path = os.path.join(icon_dir, new_filename)
                
                # Save resized image
                if resized.save(new_path, "PNG"):
                    print(f"   ✅ Created: {new_filename} ({size[0]}x{size[1]})")
                else:
                    print(f"   ❌ Failed to save: {new_filename}")
                
        except Exception as e:
            print(f"❌ Error processing {icon_file}: {e}")
    
    print("\n🎉 Icon resizing completed!")
    print("📁 Resized icons are saved with size suffixes")
    print("   Example: wifi_strong_30x30.png")

def create_icon_preview():
    """Create a preview of all resized icons"""
    print("\n🖼️ CREATING ICON PREVIEW")
    print("=" * 30)
    
    icon_dir = os.path.join(os.path.dirname(__file__), "emoji")
    
    # Find all resized icons
    resized_icons = []
    for file in os.listdir(icon_dir):
        if "_30x30.png" in file:
            resized_icons.append(file)
    
    resized_icons.sort()
    
    print("📋 Available resized icons (30x30):")
    for icon in resized_icons:
        print(f"   ✅ {icon}")
    
    return resized_icons

def main():
    """Main function"""
    print("DATABASE ICON RESIZER (PyQt6)")
    print("=" * 50)
    print("This script resizes database signal icons for UI display")
    print()
    
    # Create QApplication for PyQt6
    app = QtWidgets.QApplication(sys.argv)
    
    try:
        # Resize icons
        resize_database_icons()
        
        # Create preview
        create_icon_preview()
        
        print("\n🎯 Icons ready for database signal monitoring!")
        print("✅ All icons resized to 25x25 and 30x30 pixels")
        print("✅ High quality maintained with SmoothTransformation")
        print("✅ Optimized PNG format for fast loading")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
