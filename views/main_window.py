import os
from typing import List, Optional
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
import pandas as pd
from models.smtp_server import SMTPServer
from models.email_sender import EmailSender
from models.settings import Settings
from views.dialogs import AddSMTPDialog, DeliveryOptionsDialog
from . import resources_rc  # Import from current package
from .main_window_ui import MainWindowUI

class MainWindow(MainWindowUI):
    """Main window of the email sender application."""

    def __init__(self):
        super().__init__()  # Initialize parent class
        self.smtp_servers: List[SMTPServer] = []
        self.smtp_layouts: List[QHBoxLayout] = []  # Store layouts for removal
        self.daily_limit = 0
        self.hourly_limit = 0
        self.email_sender: Optional[EmailSender] = None
        self.settings = Settings()  # Initialize settings manager
        
        # Set up the UI first
        self.setup_ui()
        
        # Now set up connections
        self.setup_connections()
        
        # Finally load settings after UI is ready
        self.load_settings()

    def load_theme(self):
        """Load the saved theme or default to light theme."""
        theme = self.settings.get_theme()
        self.change_theme(theme)

    def change_theme(self, theme: str):
        """Change the application theme.
        
        Args:
            theme: Theme name ('light' or 'dark')
        """
        try:
            # Update theme actions
            self.light_theme_action.setChecked(theme == 'light')
            self.dark_theme_action.setChecked(theme == 'dark')
            
            # Load theme file
            theme_file = f'styles/{theme}.qss'
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    self.setStyleSheet(f.read())
                    
                # Save theme preference
                self.settings.set_theme(theme)
            else:
                raise FileNotFoundError(f"Theme file not found: {theme_file}")
                
        except Exception as e:
            QMessageBox.warning(self, "Theme Error", f"Failed to load theme: {str(e)}")

    def setup_connections(self):
        """Set up signal/slot connections."""
        self.add_smtp_button.clicked.connect(self.add_smtp_server)
        self.attachment_browse_button.clicked.connect(self.browse_attachment)
        self.delivery_options_button.clicked.connect(self.show_delivery_options)
        self.load_email_button.clicked.connect(self.load_emails)
        
        self.start_button.clicked.connect(self.start_sending)
        self.pause_button.clicked.connect(self.pause_sending)
        self.resume_button.clicked.connect(self.resume_sending)
        self.stop_button.clicked.connect(self.stop_sending)

    def add_smtp_server(self):
        """Add a new SMTP server configuration."""
        dialog = AddSMTPDialog(self)
        if dialog.exec_():
            smtp_server = dialog.get_smtp_server()
            self.smtp_servers.append(smtp_server)
            
            # Add server to UI
            server_layout = QHBoxLayout()
            label = QLabel(f"SMTP: {smtp_server.server}:{smtp_server.port}")
            test_button = QPushButton("Test")
            delete_button = QPushButton("Delete")
            
            test_button.clicked.connect(lambda: self.test_smtp_server(smtp_server))
            delete_button.clicked.connect(lambda: self.remove_smtp_server(smtp_server, server_layout))
            
            server_layout.addWidget(label)
            server_layout.addWidget(test_button)
            server_layout.addWidget(delete_button)
            
            self.smtp_form_layout.addLayout(server_layout)
            self.smtp_layouts.append(server_layout)
            
            # Save updated SMTP servers
            self.settings.save_smtp_servers(self.smtp_servers)

    def remove_smtp_server(self, smtp_server: SMTPServer, server_layout: QHBoxLayout):
        """Remove an SMTP server from both the list and UI.
        
        Args:
            smtp_server: The SMTP server to remove
            server_layout: The layout containing the server's UI elements
        """
        # Remove from list
        self.smtp_servers.remove(smtp_server)
        
        # Remove from UI
        while server_layout.count():
            item = server_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.smtp_layouts.remove(server_layout)
        server_layout.deleteLater()
        
        # Save updated SMTP servers
        self.settings.save_smtp_servers(self.smtp_servers)

    def test_smtp_server(self, smtp_server: SMTPServer):
        """Test the connection to an SMTP server."""
        success, message = smtp_server.test_connection()
        if success:
            QMessageBox.information(self, "SMTP Test", message)
        else:
            QMessageBox.critical(self, "SMTP Test", message)

    def browse_attachment(self):
        """Open file dialog to select an attachment."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Attachment",
            "",
            "All Files (*.*)"
        )
        if file_name:
            self.attachment_input.setText(file_name)

    def show_delivery_options(self):
        """Show the delivery options dialog."""
        dialog = DeliveryOptionsDialog(self)
        if dialog.exec_():
            options = dialog.get_delivery_options()
            self.daily_limit = options['daily_limit']
            self.hourly_limit = options['hourly_limit']
            
            # Save delivery options
            self.settings.save_email_settings(
                self.daily_limit,
                self.hourly_limit,
                self.emails_per_smtp_input.value()
            )

    def load_emails(self):
        """Load email addresses from a file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Load Email List",
            "",
            "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if not file_name:
            return

        try:
            if file_name.endswith('.txt'):
                with open(file_name, 'r') as f:
                    emails = f.read().splitlines()
            elif file_name.endswith('.csv'):
                df = pd.read_csv(file_name)
                emails = df[df.columns[0]].tolist()
            elif file_name.endswith('.xlsx'):
                df = pd.read_excel(file_name)
                emails = df[df.columns[0]].tolist()
            else:
                raise ValueError("Unsupported file format")

            self.email_input.setText('\n'.join(emails))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load emails: {str(e)}")

    def start_sending(self):
        """Start the email sending process."""
        if not self.smtp_servers:
            QMessageBox.warning(self, "Error", "Please add at least one SMTP server.")
            return

        if not self.email_input.toPlainText().strip():
            QMessageBox.warning(self, "Error", "Please add email recipients.")
            return

        # Save current settings before starting
        self.save_settings()

        self.email_sender = EmailSender(
            smtp_servers=self.smtp_servers,
            proxy_list=self.proxy_input.toPlainText().strip().split('\n') if self.use_proxy_checkbox.isChecked() else [],
            email_list=self.email_input.toPlainText().strip().split('\n'),
            sender_address=self.sender_address_input.text(),
            sender_name=self.sender_name_input.text(),
            reply_to=self.reply_to_input.text(),
            cc=self.cc_input.text(),
            bcc=self.bcc_input.text(),
            subject=self.subject_input.text(),
            email_body=self.body_input.toPlainText(),
            is_html=self.html_radio.isChecked(),
            delay=1,
            emails_per_smtp=self.emails_per_smtp_input.value(),
            use_proxy=self.use_proxy_checkbox.isChecked(),
            daily_limit=self.daily_limit,
            hourly_limit=self.hourly_limit,
            attachment_path=self.attachment_input.text()
        )

        self.email_sender.update_status.connect(self.update_status)
        self.email_sender.update_progress.connect(self.progress_bar.setValue)
        self.email_sender.update_log.connect(self.log_text.appendPlainText)
        self.email_sender.start()

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

    def pause_sending(self):
        """Pause the email sending process."""
        if self.email_sender:
            self.email_sender.pause()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)

    def resume_sending(self):
        """Resume the email sending process."""
        if self.email_sender:
            self.email_sender.resume()
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)

    def stop_sending(self):
        """Stop the email sending process."""
        if self.email_sender:
            self.email_sender.stop()
            self.progress_bar.setValue(0)
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def update_status(self, status: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {status}")

    def save_settings(self):
        """Save current settings to a file."""
        # Save SMTP servers
        self.settings.save_smtp_servers(self.smtp_servers)
        
        # Save email settings
        self.settings.save_email_settings(
            self.daily_limit,
            self.hourly_limit,
            self.emails_per_smtp_input.value()
        )
        
        # Save last used values
        self.settings.save_last_used(
            sender_address=self.sender_address_input.text(),
            sender_name=self.sender_name_input.text(),
            reply_to=self.reply_to_input.text(),
            cc=self.cc_input.text(),
            bcc=self.bcc_input.text(),
            subject=self.subject_input.text(),
            body=self.body_input.toPlainText(),
            is_html=self.html_radio.isChecked()
        )

    def load_settings(self):
        """Load settings from a file."""
        try:
            # Load SMTP servers
            self.smtp_servers = self.settings.get_smtp_servers()
            for server in self.smtp_servers:
                server_layout = QHBoxLayout()
                label = QLabel(f"SMTP: {server.server}:{server.port}")
                test_button = QPushButton("Test")
                delete_button = QPushButton("Delete")
                
                test_button.clicked.connect(lambda s=server: self.test_smtp_server(s))
                delete_button.clicked.connect(lambda s=server, l=server_layout: 
                                           self.remove_smtp_server(s, l))
                
                server_layout.addWidget(label)
                server_layout.addWidget(test_button)
                server_layout.addWidget(delete_button)
                
                self.smtp_form_layout.addLayout(server_layout)
                self.smtp_layouts.append(server_layout)
            
            # Load email settings
            email_settings = self.settings.get_email_settings()
            self.daily_limit = email_settings["daily_limit"]
            self.hourly_limit = email_settings["hourly_limit"]
            self.emails_per_smtp_input.setValue(email_settings["emails_per_smtp"])
            
            # Load last used values
            last_used = self.settings.get_last_used()
            self.sender_address_input.setText(last_used["sender_address"])
            self.sender_name_input.setText(last_used["sender_name"])
            self.reply_to_input.setText(last_used["reply_to"])
            self.cc_input.setText(last_used["cc"])
            self.bcc_input.setText(last_used["bcc"])
            self.subject_input.setText(last_used["subject"])
            self.body_input.setPlainText(last_used["body"])
            self.html_radio.setChecked(last_used["is_html"])
            self.plain_text_radio.setChecked(not last_used["is_html"])
            
            # Load theme
            self.load_theme()
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")

    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About DigitalGuards Mailer",
            "DigitalGuards Mailer v1.0\n\n"
            "A professional email marketing tool.\n\n"
            "© 2024 DigitalGuards"
        )
