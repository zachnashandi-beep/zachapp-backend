#!/usr/bin/env python3
"""
Email Service
Handles email sending using Gmail SMTP with HTML templates
"""

import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, Any
import os
import json

class EmailService:
    """Handles email sending using Gmail SMTP"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587  # TLS
        self.smtp_port_ssl = 465  # SSL
        self.sender_email = "zachapp.team@gmail.com"
        self.sender_password = self._load_gmail_password()
        self.verification_base_url = "https://zachnashandi-beep.github.io/zachapp/verify.html"
        self.reset_base_url = "https://zachnashandi-beep.github.io/zachapp/reset.html"
        
    def _setup_logger(self):
        """Setup logging for email operations"""
        logger = logging.getLogger('EmailService')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_gmail_password(self) -> Optional[str]:
        """Load Gmail password from file or environment variable"""
        # Try to load from file first
        password_file = "gmail_password.txt"
        if os.path.exists(password_file):
            try:
                with open(password_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                self.logger.error(f"Failed to read Gmail password from file: {e}")
        
        # Try environment variable
        password = os.getenv('GMAIL_PASSWORD')
        if password:
            return password
        
        self.logger.warning("Gmail password not found in file or environment variable")
        return None
    
    def _create_verification_email_html(self, username: str, verification_link: str) -> str:
        """Create HTML email template for verification"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Account</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 24px;
                    color: #34495e;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 16px;
                    text-align: center;
                    margin: 20px 0;
                    transition: background-color 0.3s;
                }}
                .button:hover {{
                    background-color: #2980b9;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #7f8c8d;
                    text-align: center;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .link {{
                    color: #3498db;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀 ZachApp</div>
                    <h1 class="title">Verify Your Account</h1>
                </div>
                
                <div class="message">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>Welcome to ZachApp! To complete your registration and start using your account, please verify your email address by clicking the button below.</p>
                </div>
                
                <div class="button-container">
                    <a href="{verification_link}" class="button">Verify My Account</a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you don't verify your account within this time, you'll need to request a new verification email.
                </div>
                
                <div class="message">
                    <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                    <p><a href="{verification_link}" class="link">{verification_link}</a></p>
                </div>
                
                <div class="footer">
                    <p>This email was sent to you because you signed up for a ZachApp account.</p>
                    <p>If you didn't create an account, please ignore this email.</p>
                    <p>© 2025 ZachApp Team. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_verification_email_text(self, username: str, verification_link: str) -> str:
        """Create plain text email template for verification"""
        return f"""
        Hello {username},
        
        Welcome to ZachApp! To complete your registration and start using your account, please verify your email address by clicking the link below:
        
        {verification_link}
        
        Important: This verification link will expire in 24 hours. If you don't verify your account within this time, you'll need to request a new verification email.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        The ZachApp Team
        
        © 2025 ZachApp Team. All rights reserved.
        """
    
    def _create_confirmation_email_html(self, username: str) -> str:
        """Create HTML email template for verification confirmation"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Verified</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 24px;
                    color: #27ae60;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .success-icon {{
                    font-size: 48px;
                    color: #27ae60;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #27ae60;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 16px;
                    text-align: center;
                    margin: 20px 0;
                    transition: background-color 0.3s;
                }}
                .button:hover {{
                    background-color: #229954;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #7f8c8d;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀 ZachApp</div>
                    <h1 class="title">Account Verified!</h1>
                </div>
                
                <div class="button-container">
                    <div class="success-icon">✅</div>
                </div>
                
                <div class="message">
                    <p>Congratulations <strong>{username}</strong>!</p>
                    <p>Your account has been successfully verified. You can now log in and start using all the features of ZachApp.</p>
                </div>
                
                <div class="button-container">
                    <a href="https://zachnashandi-beep.github.io/zachapp/login" class="button">Login to Your Account</a>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing ZachApp!</p>
                    <p>© 2025 ZachApp Team. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_confirmation_email_text(self, username: str) -> str:
        """Create plain text email template for verification confirmation"""
        return f"""
        Congratulations {username}!
        
        Your account has been successfully verified. You can now log in and start using all the features of ZachApp.
        
        Login to your account: https://zachnashandi-beep.github.io/zachapp/login
        
        Thank you for choosing ZachApp!
        
        Best regards,
        The ZachApp Team
        
        © 2025 ZachApp Team. All rights reserved.
        """
    
    def _create_reset_email_html(self, username: str, reset_link: str) -> str:
        """Create HTML email template for password reset"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 24px;
                    color: #e74c3c;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .button {{
                    display: inline-block;
                    background-color: #e74c3c;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 16px;
                    text-align: center;
                    margin: 20px 0;
                    transition: background-color 0.3s;
                }}
                .button:hover {{
                    background-color: #c0392b;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #7f8c8d;
                    text-align: center;
                }}
                .warning {{
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .security {{
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    color: #0c5460;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .link {{
                    color: #e74c3c;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀 ZachApp</div>
                    <h1 class="title">Reset Your Password</h1>
                </div>
                
                <div class="message">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>We received a request to reset your password for your ZachApp account. If you made this request, click the button below to reset your password.</p>
                    <p>Thank you for being a valued member of the ZachApp community. We're committed to providing you with a secure and seamless experience, and we're here to help you regain access to your account quickly and safely.</p>
                </div>
                
                <div class="button-container">
                    <a href="{reset_link}" class="button">Reset My Password</a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> This password reset link will expire in 1 hour for security reasons. If you don't reset your password within this time, you'll need to request a new reset link.
                </div>
                
                <div class="security">
                    <strong>🔒 Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged. For additional security, consider changing your password if you suspect unauthorized access to your account.
                </div>
                
                <div class="message">
                    <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                    <p><a href="{reset_link}" class="link">{reset_link}</a></p>
                </div>
                
                <div class="footer">
                    <p>This email was sent to you because a password reset was requested for your ZachApp account.</p>
                    <p>If you didn't request this reset, please ignore this email and consider changing your password for security.</p>
                    <p><strong>Need help?</strong> Contact our support team at zachapp.team@gmail.com</p>
                    <p>Thank you for choosing ZachApp! We appreciate your trust in our platform.</p>
                    <p>© 2025 ZachApp Team. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_reset_email_text(self, username: str, reset_link: str) -> str:
        """Create plain text email template for password reset"""
        return f"""
        Hello {username},
        
        We received a request to reset your password for your ZachApp account. If you made this request, click the link below to reset your password:
        
        {reset_link}
        
        Thank you for being a valued member of the ZachApp community. We're committed to providing you with a secure and seamless experience, and we're here to help you regain access to your account quickly and safely.
        
        Important: This password reset link will expire in 1 hour for security reasons. If you don't reset your password within this time, you'll need to request a new reset link.
        
        Security Notice: If you didn't request this password reset, please ignore this email and consider changing your password for security. Your password will remain unchanged unless you use this link.
        
        Need help? Contact our support team at zachapp.team@gmail.com
        
        Thank you for choosing ZachApp! We appreciate your trust in our platform.
        
        Best regards,
        The ZachApp Team
        
        © 2025 ZachApp Team. All rights reserved.
        """
    
    def send_verification_email(self, username: str, email: str, token: str) -> bool:
        """Send verification email to user"""
        try:
            if not self.sender_password:
                self.logger.error("Gmail password not configured")
                return False
            
            # Create verification link
            verification_link = f"{self.verification_base_url}?username={username}&token={token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your ZachApp Account"
            message["From"] = self.sender_email
            message["To"] = email
            
            # Create HTML and text versions
            html_content = self._create_verification_email_html(username, verification_link)
            text_content = self._create_verification_email_text(username, verification_link)
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            return self._send_email(message, email)
            
        except Exception as e:
            self.logger.error(f"Failed to send verification email to {email}: {e}")
            return False
    
    def send_reset_email(self, username: str, email: str, token: str) -> bool:
        """Send password reset email to user"""
        try:
            if not self.sender_password:
                self.logger.error("Gmail password not configured")
                return False
            
            # Create reset link
            reset_link = f"{self.reset_base_url}?username={username}&token={token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your ZachApp Password"
            message["From"] = self.sender_email
            message["To"] = email
            
            # Create HTML and text versions
            html_content = self._create_reset_email_html(username, reset_link)
            text_content = self._create_reset_email_text(username, reset_link)
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            return self._send_email(message, email)
            
        except Exception as e:
            self.logger.error(f"Failed to send reset email to {email}: {e}")
            return False
    
    def send_confirmation_email(self, username: str, email: str) -> bool:
        """Send confirmation email after successful verification"""
        try:
            if not self.sender_password:
                self.logger.error("Gmail password not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Account Verified - Welcome to ZachApp!"
            message["From"] = self.sender_email
            message["To"] = email
            
            # Create HTML and text versions
            html_content = self._create_confirmation_email_html(username)
            text_content = self._create_confirmation_email_text(username)
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            return self._send_email(message, email)
            
        except Exception as e:
            self.logger.error(f"Failed to send confirmation email to {email}: {e}")
            return False
    
    def _send_email(self, message: MIMEMultipart, recipient: str) -> bool:
        """Send email using Gmail SMTP"""
        try:
            # Create secure connection
            context = ssl.create_default_context()
            
            # Try TLS first
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
                    self.logger.info(f"✅ Email sent successfully to {recipient} via TLS")
                    return True
            except Exception as tls_error:
                self.logger.warning(f"TLS failed, trying SSL: {tls_error}")
                
                # Try SSL as fallback
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl, context=context) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
                    self.logger.info(f"✅ Email sent successfully to {recipient} via SSL")
                    return True
                    
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Authentication failed: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"Recipient refused: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP Server disconnected: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """Test Gmail SMTP connection"""
        try:
            if not self.sender_password:
                self.logger.error("Gmail password not configured")
                return False
            
            context = ssl.create_default_context()
            
            # Try TLS
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.sender_email, self.sender_password)
                    self.logger.info("✅ Gmail SMTP connection successful via TLS")
                    return True
            except Exception as tls_error:
                self.logger.warning(f"TLS failed, trying SSL: {tls_error}")
                
                # Try SSL
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl, context=context) as server:
                    server.login(self.sender_email, self.sender_password)
                    self.logger.info("✅ Gmail SMTP connection successful via SSL")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Gmail SMTP connection failed: {e}")
            return False
    
    def get_email_status(self) -> Dict[str, Any]:
        """Get email service status"""
        return {
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "sender_email": self.sender_email,
            "password_configured": self.sender_password is not None,
            "verification_base_url": self.verification_base_url,
            "reset_base_url": self.reset_base_url
        }

# Global email service instance
email_service = EmailService()

# Convenience functions
def send_verification_email(username: str, email: str, token: str) -> bool:
    """Send verification email to user"""
    return email_service.send_verification_email(username, email, token)

def send_reset_email(username: str, email: str, token: str) -> bool:
    """Send password reset email to user"""
    return email_service.send_reset_email(username, email, token)

def send_confirmation_email(username: str, email: str) -> bool:
    """Send confirmation email after successful verification"""
    return email_service.send_confirmation_email(username, email)

def test_email_connection() -> bool:
    """Test Gmail SMTP connection"""
    return email_service.test_email_connection()

def get_email_status() -> Dict[str, Any]:
    """Get email service status"""
    return email_service.get_email_status()

if __name__ == "__main__":
    # Test the email service
    print("Testing Email Service...")
    
    # Check status
    status = get_email_status()
    print(f"SMTP Server: {status['smtp_server']}")
    print(f"SMTP Port: {status['smtp_port']}")
    print(f"Sender Email: {status['sender_email']}")
    print(f"Password Configured: {status['password_configured']}")
    print(f"Verification Base URL: {status['verification_base_url']}")
    
    # Test connection
    if status['password_configured']:
        print("\nTesting Gmail SMTP connection...")
        connection_success = test_email_connection()
        print(f"Connection test: {'✅ Success' if connection_success else '❌ Failed'}")
    else:
        print("\n❌ Gmail password not configured")
        print("Please set up gmail_password.txt or GMAIL_PASSWORD environment variable")
