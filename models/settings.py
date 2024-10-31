import json
import os
from typing import List, Dict, Any, Optional
from .smtp_server import SMTPServer
import base64

class Settings:
    """Handles application settings storage and retrieval."""
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "theme": "light",
            "smtp_servers": [],
            "email_settings": {
                "daily_limit": 0,
                "hourly_limit": 0,
                "emails_per_smtp": 50
            },
            "last_used": {
                "sender_address": "",
                "sender_name": "",
                "reply_to": "",
                "cc": "",
                "bcc": "",
                "subject": "",
                "body": "",
                "is_html": False
            }
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create with defaults if not exists."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Decrypt SMTP passwords
                    if "smtp_servers" in settings:
                        for server in settings["smtp_servers"]:
                            if "password" in server:
                                server["password"] = self._decrypt_password(server["password"])
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file."""
        try:
            # Create a copy of settings for saving
            settings_to_save = self.settings.copy()
            
            # Encrypt SMTP passwords for storage
            if "smtp_servers" in settings_to_save:
                settings_to_save["smtp_servers"] = [
                    {**server, "password": self._encrypt_password(server["password"])}
                    for server in settings_to_save["smtp_servers"]
                ]
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _encrypt_password(self, password: str) -> str:
        """Simple base64 encoding for passwords."""
        return base64.b64encode(password.encode()).decode()

    def _decrypt_password(self, encrypted: str) -> str:
        """Decrypt base64 encoded passwords."""
        return base64.b64decode(encrypted.encode()).decode()

    def get_theme(self) -> str:
        """Get current theme setting."""
        return self.settings.get("theme", "light")

    def set_theme(self, theme: str):
        """Set theme setting."""
        self.settings["theme"] = theme
        self.save_settings()

    def get_smtp_servers(self) -> List[SMTPServer]:
        """Get list of SMTP server configurations."""
        servers = self.settings.get("smtp_servers", [])
        return [SMTPServer(**server) for server in servers]

    def save_smtp_servers(self, servers: List[SMTPServer]):
        """Save SMTP server configurations."""
        self.settings["smtp_servers"] = [
            {
                "server": s.server,
                "port": s.port,
                "username": s.username,
                "password": s.password,
                "tls_mode": s.tls_mode
            }
            for s in servers
        ]
        self.save_settings()

    def get_email_settings(self) -> Dict[str, int]:
        """Get email sending settings."""
        return self.settings.get("email_settings", self.default_settings["email_settings"])

    def save_email_settings(self, daily_limit: int, hourly_limit: int, emails_per_smtp: int):
        """Save email sending settings."""
        self.settings["email_settings"] = {
            "daily_limit": daily_limit,
            "hourly_limit": hourly_limit,
            "emails_per_smtp": emails_per_smtp
        }
        self.save_settings()

    def get_last_used(self) -> Dict[str, Any]:
        """Get last used email settings."""
        return self.settings.get("last_used", self.default_settings["last_used"])

    def save_last_used(self, 
                      sender_address: str,
                      sender_name: Optional[str] = None,
                      reply_to: Optional[str] = None,
                      cc: Optional[str] = None,
                      bcc: Optional[str] = None,
                      subject: Optional[str] = None,
                      body: Optional[str] = None,
                      is_html: Optional[bool] = None):
        """Save last used email settings."""
        last_used = self.settings.get("last_used", {})
        
        if sender_address: last_used["sender_address"] = sender_address
        if sender_name is not None: last_used["sender_name"] = sender_name
        if reply_to is not None: last_used["reply_to"] = reply_to
        if cc is not None: last_used["cc"] = cc
        if bcc is not None: last_used["bcc"] = bcc
        if subject is not None: last_used["subject"] = subject
        if body is not None: last_used["body"] = body
        if is_html is not None: last_used["is_html"] = is_html
        
        self.settings["last_used"] = last_used
        self.save_settings()
