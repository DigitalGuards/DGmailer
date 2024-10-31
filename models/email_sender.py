from typing import List, Optional, Dict
from datetime import datetime, timedelta
import time
import smtplib
import socks
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from models.smtp_server import SMTPServer

class SMTPRotator:
    """Manages SMTP server rotation with usage tracking and health checks."""
    def __init__(self, smtp_servers: List[SMTPServer], emails_per_smtp: int):
        self.smtp_servers = smtp_servers
        self.emails_per_smtp = emails_per_smtp
        self.current_index = 0
        self.server_stats: Dict[int, Dict] = {}
        self.initialize_stats()

    def initialize_stats(self):
        """Initialize statistics for each SMTP server."""
        for i in range(len(self.smtp_servers)):
            self.server_stats[i] = {
                'emails_sent': 0,
                'last_used': None,
                'errors': 0,
                'consecutive_errors': 0,
                'cooldown_until': None
            }

    def should_rotate(self) -> bool:
        """Check if we should rotate to the next SMTP server."""
        if not self.server_stats[self.current_index].get('last_used'):
            return False
            
        stats = self.server_stats[self.current_index]
        
        # Rotate if we've hit the email limit for this server
        if stats['emails_sent'] >= self.emails_per_smtp:
            return True
            
        # Rotate if we've had too many consecutive errors
        if stats['consecutive_errors'] >= 3:
            return True
            
        # Rotate if server is in cooldown
        if stats['cooldown_until'] and datetime.now() < stats['cooldown_until']:
            return True
            
        return False

    def get_next_server(self) -> tuple[SMTPServer, int]:
        """Get the next available SMTP server."""
        original_index = self.current_index
        
        while True:
            if self.should_rotate():
                self.current_index = (self.current_index + 1) % len(self.smtp_servers)
                
                # If we've checked all servers and come back to the start, reset stats
                if self.current_index == original_index:
                    self.reset_server_stats(original_index)
                    break
                    
                # Skip servers in cooldown
                stats = self.server_stats[self.current_index]
                if stats['cooldown_until'] and datetime.now() < stats['cooldown_until']:
                    continue
                    
                # Reset stats for the new server
                self.reset_server_stats(self.current_index)
                break
            else:
                break
                
        return self.smtp_servers[self.current_index], self.current_index

    def record_success(self, server_index: int):
        """Record a successful email send for a server."""
        stats = self.server_stats[server_index]
        stats['emails_sent'] += 1
        stats['last_used'] = datetime.now()
        stats['consecutive_errors'] = 0

    def record_error(self, server_index: int):
        """Record an error for a server."""
        stats = self.server_stats[server_index]
        stats['errors'] += 1
        stats['consecutive_errors'] += 1
        
        # If too many consecutive errors, put server in cooldown
        if stats['consecutive_errors'] >= 3:
            stats['cooldown_until'] = datetime.now() + timedelta(minutes=15)

    def reset_server_stats(self, server_index: int):
        """Reset statistics for a specific server."""
        self.server_stats[server_index] = {
            'emails_sent': 0,
            'last_used': None,
            'errors': 0,
            'consecutive_errors': 0,
            'cooldown_until': None
        }

class ProxyRotator:
    """Manages proxy rotation with health tracking."""
    
    def __init__(self, proxy_list: List[str]):
        self.proxy_list = proxy_list
        self.current_index = 0
        self.proxy_stats: Dict[int, Dict] = {}
        self.initialize_stats()

    def initialize_stats(self):
        """Initialize statistics for each proxy."""
        for i in range(len(self.proxy_list)):
            self.proxy_stats[i] = {
                'uses': 0,
                'errors': 0,
                'consecutive_errors': 0,
                'cooldown_until': None
            }

    def get_next_proxy(self) -> tuple[str, int]:
        """Get the next available proxy."""
        if not self.proxy_list:
            return None, -1
            
        original_index = self.current_index
        
        while True:
            stats = self.proxy_stats[self.current_index]
            
            # Skip proxies in cooldown
            if stats['cooldown_until'] and datetime.now() < stats['cooldown_until']:
                self.current_index = (self.current_index + 1) % len(self.proxy_list)
                
                # If we've checked all proxies and come back to start
                if self.current_index == original_index:
                    # Reset cooldown for the least problematic proxy
                    best_proxy = min(self.proxy_stats.items(), 
                                   key=lambda x: x[1]['errors'])
                    self.reset_proxy_stats(best_proxy[0])
                    return self.proxy_list[best_proxy[0]], best_proxy[0]
            else:
                break
                
        proxy = self.proxy_list[self.current_index]
        current = self.current_index
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return proxy, current

    def record_error(self, proxy_index: int):
        """Record an error for a proxy."""
        if proxy_index == -1:
            return
            
        stats = self.proxy_stats[proxy_index]
        stats['errors'] += 1
        stats['consecutive_errors'] += 1
        
        # If too many consecutive errors, put proxy in cooldown
        if stats['consecutive_errors'] >= 3:
            stats['cooldown_until'] = datetime.now() + timedelta(minutes=30)

    def record_success(self, proxy_index: int):
        """Record a successful use of a proxy."""
        if proxy_index == -1:
            return
            
        stats = self.proxy_stats[proxy_index]
        stats['uses'] += 1
        stats['consecutive_errors'] = 0

    def reset_proxy_stats(self, proxy_index: int):
        """Reset statistics for a specific proxy."""
        self.proxy_stats[proxy_index] = {
            'uses': 0,
            'errors': 0,
            'consecutive_errors': 0,
            'cooldown_until': None
        }

class EmailSender(QThread):
    """Thread for handling email sending operations."""
    
    # Signals for UI updates
    update_status = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    reset_progress = pyqtSignal()

    def __init__(self,
                 smtp_servers: List[SMTPServer],
                 proxy_list: List[str],
                 email_list: List[str],
                 sender_address: str,
                 sender_name: Optional[str],
                 reply_to: Optional[str],
                 cc: Optional[str],
                 bcc: Optional[str],
                 subject: str,
                 email_body: str,
                 is_html: bool,
                 delay: int,
                 emails_per_smtp: int,
                 use_proxy: bool,
                 daily_limit: int,
                 hourly_limit: int,
                 attachment_path: Optional[str]):
        """Initialize the email sender thread.

        Args:
            smtp_servers: List of SMTP server configurations
            proxy_list: List of proxy servers to use
            email_list: List of recipient email addresses
            sender_address: Email address of the sender
            sender_name: Display name of the sender
            reply_to: Reply-to email address
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            subject: Email subject
            email_body: Email body content
            is_html: Whether the email body is HTML
            delay: Delay between emails in seconds
            emails_per_smtp: Number of emails to send per SMTP server
            use_proxy: Whether to use proxy servers
            daily_limit: Maximum emails per day (0 for no limit)
            hourly_limit: Maximum emails per hour (0 for no limit)
            attachment_path: Path to file to attach to emails
        """
        super().__init__()
        
        # Email configuration
        self.smtp_servers = smtp_servers
        self.proxy_list = proxy_list
        self.email_list = email_list
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.reply_to = reply_to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.email_body = email_body
        self.is_html = is_html
        self.attachment_path = attachment_path
        
        # Sending configuration
        self.delay = delay
        self.emails_per_smtp = emails_per_smtp
        self.use_proxy = use_proxy
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
        
        # Initialize rotators
        self.smtp_rotator = SMTPRotator(smtp_servers, emails_per_smtp)
        self.proxy_rotator = ProxyRotator(proxy_list) if use_proxy else None
        
        # Thread control
        self.stop_thread = False
        self.pause_thread = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def setup_proxy(self, proxy: str) -> bool:
        """Set up the proxy for email sending."""
        if not proxy:
            return True
            
        try:
            proxy_host, proxy_port = proxy.split(':')
            socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_host, int(proxy_port))
            socks.wrapmodule(smtplib)
            self.update_log.emit(f"Using proxy {proxy_host}:{proxy_port}")
            return True
        except Exception as e:
            self.update_log.emit(f"Failed to set up proxy {proxy}: {str(e)}")
            return False

    def run(self):
        """Main email sending loop."""
        emails_sent = 0
        hourly_sent = 0
        daily_sent = 0
        total_emails = len(self.email_list)
        
        start_time = datetime.now()
        hourly_reset = start_time + timedelta(hours=1)
        daily_reset = start_time + timedelta(days=1)

        for email in self.email_list:
            if self.stop_thread:
                break

            # Handle pause state
            if self.pause_thread:
                self.mutex.lock()
                self.condition.wait(self.mutex)
                self.mutex.unlock()

            # Check and reset limits
            current_time = datetime.now()
            
            # Reset hourly counter if needed
            if current_time >= hourly_reset:
                hourly_sent = 0
                hourly_reset = current_time + timedelta(hours=1)
                
            # Reset daily counter if needed
            if current_time >= daily_reset:
                daily_sent = 0
                daily_reset = current_time + timedelta(days=1)

            # Check limits
            if self.hourly_limit and hourly_sent >= self.hourly_limit:
                wait_seconds = int((hourly_reset - current_time).total_seconds())
                self.update_status.emit(
                    f"Hourly limit reached. Pausing for {wait_seconds} seconds."
                )
                time.sleep(wait_seconds)
                hourly_sent = 0
                continue

            if self.daily_limit and daily_sent >= self.daily_limit:
                wait_seconds = int((daily_reset - current_time).total_seconds())
                self.update_status.emit(
                    f"Daily limit reached. Pausing for {wait_seconds} seconds."
                )
                time.sleep(wait_seconds)
                daily_sent = 0
                continue

            # Get next SMTP server and proxy
            smtp_server, smtp_index = self.smtp_rotator.get_next_server()
            proxy, proxy_index = (self.proxy_rotator.get_next_proxy() 
                                if self.use_proxy else (None, -1))

            # Set up proxy if needed
            if self.use_proxy and not self.setup_proxy(proxy):
                self.proxy_rotator.record_error(proxy_index)
                continue

            # Send email
            success, message = smtp_server.send_email(
                self.sender_address,
                self.sender_name,
                email,
                self.subject,
                self.email_body,
                self.is_html,
                self.reply_to,
                self.cc,
                self.bcc,
                self.attachment_path
            )

            # Record results
            if success:
                self.smtp_rotator.record_success(smtp_index)
                if self.use_proxy:
                    self.proxy_rotator.record_success(proxy_index)
                emails_sent += 1
                hourly_sent += 1
                daily_sent += 1
            else:
                self.smtp_rotator.record_error(smtp_index)
                if self.use_proxy:
                    self.proxy_rotator.record_error(proxy_index)

            # Update progress
            progress = int((emails_sent / total_emails) * 100)
            self.update_progress.emit(progress)
            
            # Log result
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = "Success" if success else f"Failed: {message}"
            self.update_log.emit(f"{timestamp} - Email to {email}: {status}")

            # Delay before next email if not stopping
            if not self.stop_thread and emails_sent < total_emails:
                time.sleep(self.delay)

        # Clean up
        self.update_status.emit("Email sending completed")
        self.reset_progress.emit()

    def stop(self):
        """Stop the email sending process."""
        self.stop_thread = True
        self.condition.wakeAll()

    def pause(self):
        """Pause the email sending process."""
        self.pause_thread = True
        self.update_status.emit("Email sending paused")

    def resume(self):
        """Resume the email sending process."""
        self.pause_thread = False
        self.condition.wakeAll()
        self.update_status.emit("Email sending resumed")
