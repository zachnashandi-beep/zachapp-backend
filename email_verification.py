import os
import json
import time
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

class EmailVerificationManager:
    """Manages email verification for user accounts"""
    
    def __init__(self, verification_file: str = "verification.json"):
        self.verification_file = verification_file
        self.default_expiry = 24 * 3600  # 24 hours in seconds
        
        # Email configuration (you'll need to set these)
        self.smtp_server = "smtp.gmail.com"  # Change to your SMTP server
        self.smtp_port = 587
        self.sender_email = "your-email@gmail.com"  # Change to your email
        self.sender_password = "your-app-password"  # Change to your app password
        self.app_url = "https://yourapp.com"  # Change to your app URL
    
    def _load_verifications(self) -> Dict:
        """Load verification data from JSON file"""
        try:
            if not os.path.exists(self.verification_file):
                return {}
            with open(self.verification_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load verifications: {e}")
            return {}
    
    def _save_verifications(self, verifications: Dict) -> bool:
        """Save verification data to JSON file"""
        try:
            with open(self.verification_file, "w", encoding="utf-8") as f:
                json.dump(verifications, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save verifications: {e}")
            return False
    
    def generate_verification_token(self, username: str, expiry_hours: int = 24) -> str:
        """
        Generate a verification token for a user
        
        Args:
            username: The username to generate token for
            expiry_hours: Hours until token expires (default: 24)
            
        Returns:
            str: The generated verification token
        """
        # Generate secure token
        token = secrets.token_hex(32)
        expiry = int(time.time()) + (expiry_hours * 3600)
        
        # Load existing verifications
        verifications = self._load_verifications()
        
        # Create/update verification entry
        verifications[username] = {
            "token": token,
            "expiry": expiry,
            "verified": False,
            "created": int(time.time())
        }
        
        # Save verifications
        if self._save_verifications(verifications):
            print(f"DEBUG: Generated verification token for {username}, expires at {expiry}")
            return token
        else:
            raise Exception("Failed to save verification token")
    
    def verify_email(self, username: str, token: str) -> bool:
        """
        Verify a user's email with the provided token
        
        Args:
            username: The username to verify
            token: The verification token
            
        Returns:
            bool: True if verification succeeded, False otherwise
        """
        verifications = self._load_verifications()
        current_time = int(time.time())
        
        # Check if user has a verification entry
        if username not in verifications:
            print(f"DEBUG: No verification found for {username}")
            return False
        
        verification_data = verifications[username]
        
        # Check if already verified
        if verification_data.get("verified", False):
            print(f"DEBUG: User {username} is already verified")
            return True
        
        # Check if token matches
        if verification_data.get("token") != token:
            print(f"DEBUG: Token mismatch for {username}")
            return False
        
        # Check if token is expired
        if current_time > verification_data.get("expiry", 0):
            print(f"DEBUG: Verification token expired for {username}")
            # Remove expired verification
            del verifications[username]
            self._save_verifications(verifications)
            return False
        
        # Mark as verified
        verifications[username]["verified"] = True
        verifications[username]["verified_at"] = current_time
        
        if self._save_verifications(verifications):
            print(f"DEBUG: Email verified for {username}")
            return True
        else:
            print(f"DEBUG: Failed to mark {username} as verified")
            return False
    
    def is_verified(self, username: str) -> bool:
        """
        Check if a user's email is verified
        
        Args:
            username: The username to check
            
        Returns:
            bool: True if verified, False otherwise
        """
        verifications = self._load_verifications()
        
        if username not in verifications:
            return False
        
        return verifications[username].get("verified", False)
    
    def get_verification_info(self, username: str) -> Optional[Dict]:
        """
        Get verification information for a user
        
        Args:
            username: The username to get info for
            
        Returns:
            Dict with verification info or None if no verification
        """
        verifications = self._load_verifications()
        return verifications.get(username)
    
    def resend_verification(self, username: str, expiry_hours: int = 24) -> str:
        """
        Generate a new verification token for a user
        
        Args:
            username: The username to resend verification for
            expiry_hours: Hours until new token expires
            
        Returns:
            str: The new verification token
        """
        return self.generate_verification_token(username, expiry_hours)
    
    def cleanup_expired_verifications(self) -> int:
        """
        Remove all expired verification tokens
        
        Returns:
            int: Number of verifications cleaned up
        """
        verifications = self._load_verifications()
        current_time = int(time.time())
        expired_users = []
        
        for username, verification_data in verifications.items():
            # Only remove unverified expired tokens
            if not verification_data.get("verified", False) and current_time > verification_data.get("expiry", 0):
                expired_users.append(username)
        
        for username in expired_users:
            del verifications[username]
        
        if expired_users:
            self._save_verifications(verifications)
            print(f"DEBUG: Cleaned up {len(expired_users)} expired verifications")
        
        return len(expired_users)
    
    def send_verification_email(self, username: str, email: str, token: str) -> bool:
        """
        Send verification email to user
        
        Args:
            username: The username
            email: The user's email address
            token: The verification token
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Create verification link
            verification_link = f"{self.app_url}/verify?{urlencode({'user': username, 'token': token})}"
            
            # Create email content
            subject = "Email Verification Required"
            
            html_body = f"""
            <html>
            <body>
                <h2>Email Verification</h2>
                <p>Hello {username},</p>
                <p>Thank you for signing up! Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Your App Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Email Verification
            
            Hello {username},
            
            Thank you for signing up! Please verify your email address by visiting the link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            
            Best regards,
            Your App Team
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = email
            
            # Add both plain text and HTML versions
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"DEBUG: Verification email sent to {email}")
            return True
            
        except Exception as e:
            print(f"Error: Failed to send verification email: {e}")
            return False
    
    def send_verification_email_simulation(self, username: str, email: str, token: str) -> bool:
        """
        Simulate sending verification email (for demo purposes)
        
        Args:
            username: The username
            email: The user's email address
            token: The verification token
            
        Returns:
            bool: True if simulation successful
        """
        # Create verification link
        verification_link = f"{self.app_url}/verify?{urlencode({'user': username, 'token': token})}"
        
        print("=" * 60)
        print("EMAIL VERIFICATION SIMULATION")
        print("=" * 60)
        print(f"To: {email}")
        print(f"Subject: Email Verification Required")
        print()
        print(f"Hello {username},")
        print()
        print("Thank you for signing up! Please verify your email address by clicking the link below:")
        print()
        print(f"VERIFICATION LINK: {verification_link}")
        print()
        print("This link will expire in 24 hours.")
        print()
        print("If you didn't create an account, please ignore this email.")
        print()
        print("Best regards,")
        print("Your App Team")
        print("=" * 60)
        
        return True


# Global verification manager instance
verification_manager = EmailVerificationManager()


def generate_verification_token(username: str, expiry_hours: int = 24) -> str:
    """Convenience function to generate verification token"""
    return verification_manager.generate_verification_token(username, expiry_hours)


def verify_email(username: str, token: str) -> bool:
    """Convenience function to verify email"""
    return verification_manager.verify_email(username, token)


def is_verified(username: str) -> bool:
    """Convenience function to check if user is verified"""
    return verification_manager.is_verified(username)


def resend_verification(username: str, expiry_hours: int = 24) -> str:
    """Convenience function to resend verification"""
    return verification_manager.resend_verification(username, expiry_hours)


def send_verification_email(username: str, email: str, token: str) -> bool:
    """Convenience function to send verification email"""
    return verification_manager.send_verification_email(username, email, token)


def send_verification_email_simulation(username: str, email: str, token: str) -> bool:
    """Convenience function to simulate sending verification email"""
    return verification_manager.send_verification_email_simulation(username, email, token)


def cleanup_expired_verifications() -> int:
    """Convenience function to cleanup expired verifications"""
    return verification_manager.cleanup_expired_verifications()


# Demo function to show usage
def demo_email_verification():
    """Demonstrate email verification functionality"""
    print("=" * 60)
    print("EMAIL VERIFICATION DEMO")
    print("=" * 60)
    
    username = "demo_user"
    email = "demo@example.com"
    
    # Clean up any existing verifications
    print("\n1. Cleaning up expired verifications...")
    cleaned = cleanup_expired_verifications()
    print(f"   Cleaned up {cleaned} expired verifications")
    
    # Generate verification token
    print(f"\n2. Generating verification token for '{username}'...")
    token = generate_verification_token(username, 24)
    print(f"   Token: {token[:16]}...")
    
    # Check verification status
    print(f"\n3. Checking verification status for '{username}'...")
    if is_verified(username):
        print("   ✅ User is verified")
    else:
        print("   ❌ User is not verified")
    
    # Send verification email (real email)
    print(f"\n4. Sending verification email to '{email}'...")
    if send_verification_email(username, email, token):
        print("   ✅ Verification email sent")
    else:
        print("   ❌ Failed to send verification email")
    
    # Try to verify with correct token
    print(f"\n5. Verifying email with correct token...")
    if verify_email(username, token):
        print("   ✅ Email verified successfully")
    else:
        print("   ❌ Email verification failed")
    
    # Check verification status again
    print(f"\n6. Checking verification status after verification...")
    if is_verified(username):
        print("   ✅ User is now verified")
    else:
        print("   ❌ User is still not verified")
    
    # Try to verify again (should still work)
    print(f"\n7. Trying to verify again (should still work)...")
    if verify_email(username, token):
        print("   ✅ Already verified user can still verify")
    else:
        print("   ❌ Already verified user cannot verify again")
    
    # Try to verify with wrong token
    print(f"\n8. Trying to verify with wrong token...")
    wrong_token = "wrong_token_12345"
    if not verify_email(username, wrong_token):
        print("   ✅ Wrong token correctly rejected")
    else:
        print("   ❌ Wrong token incorrectly accepted")
    
    # Try to verify non-existent user
    print(f"\n9. Trying to verify non-existent user...")
    if not verify_email("nonexistent_user", token):
        print("   ✅ Non-existent user correctly rejected")
    else:
        print("   ❌ Non-existent user incorrectly accepted")
    
    print("\n" + "=" * 60)
    print("EMAIL VERIFICATION DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_email_verification()
