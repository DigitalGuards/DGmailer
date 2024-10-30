import os
from typing import List, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QTextEdit, QPushButton,
                            QProgressBar, QFileDialog, QMessageBox, QCheckBox,
                            QSpinBox, QTabWidget, QGroupBox, QGridLayout,
                            QPlainTextEdit, QMenuBar, QMenu, QAction,
                            QButtonGroup, QRadioButton, QFormLayout)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap
import pandas as pd
from models.smtp_server import SMTPServer
from models.email_sender import EmailSender
from views.dialogs import AddSMTPDialog, DeliveryOptionsDialog
from . import resources_rc  # Import from current package

class MainWindow(QMainWindow):
    """Main window of the email sender application."""

    def __init__(self):
        super().__init__()
        self.smtp_servers: List[SMTPServer] = []
        self.smtp_layouts: List[QHBoxLayout] = []  # Store layouts for removal
        self.daily_limit = 0
        self.hourly_limit = 0
        self.email_sender: Optional[EmailSender] = None
        self.settings = QSettings('DigitalGuards', 'Mailer')
        
        self.setup_ui()
        self.load_theme()
        self.setup_connections()

    def setup_ui(self):
        """Set up the main window's user interface."""
        self.setWindowTitle("DigitalGuards Mailer")
        self.setMinimumSize(1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(":/resources/images/logo.png")
        scaled_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Set up menu bar
        self.create_menu_bar()

        # Create tab widget
        self.tabs = QTabWidget()
        self.setup_main_tab()
        self.setup_email_list_tab()
        self.setup_log_tab()
        self.setup_proxy_tab()

        main_layout.addWidget(self.tabs)

    def create_menu_bar(self):
        """Create the application menu bar."""
        self.menubar = self.menuBar()
        
        # File menu
        file_menu = self.menubar.addMenu('&File')
        
        save_action = QAction(QIcon(':/icons/save.png'), '&Save Settings', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_action)
        
        load_action = QAction(QIcon(':/icons/load.png'), '&Load Settings', self)
        load_action.setShortcut('Ctrl+L')
        load_action.triggered.connect(self.load_settings)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(QIcon(':/icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = self.menubar.addMenu('&View')
        
        # Theme submenu
        theme_menu = view_menu.addMenu('&Theme')
        
        self.light_theme_action = QAction('&Light', self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(self.light_theme_action)
        
        self.dark_theme_action = QAction('&Dark', self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        theme_menu.addAction(self.dark_theme_action)
        
        # Help menu
        help_menu = self.menubar.addMenu('&Help')
        
        about_action = QAction(QIcon(':/icons/about.png'), '&About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def load_theme(self):
        """Load the saved theme or default to light theme."""
        theme = self.settings.value('theme', 'light')
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
                self.settings.setValue('theme', theme)
                self.settings.sync()
            else:
                raise FileNotFoundError(f"Theme file not found: {theme_file}")
                
        except Exception as e:
            QMessageBox.warning(self, "Theme Error", f"Failed to load theme: {str(e)}")

    def setup_main_tab(self):
        """Set up the main tab with email sending controls."""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)

        # Split into left and right sections
        h_layout = QHBoxLayout()

        # Left section (SMTP and Email settings)
        left_layout = QVBoxLayout()

        # SMTP Settings Group
        smtp_group = QGroupBox("SMTP Settings")
        smtp_layout = QVBoxLayout()
        self.smtp_form_layout = QVBoxLayout()
        smtp_layout.addLayout(self.smtp_form_layout)
        self.add_smtp_button = QPushButton('Add SMTP Server')
        smtp_layout.addWidget(self.add_smtp_button)
        smtp_group.setLayout(smtp_layout)

        # Email Settings Group
        email_group = QGroupBox("Email Settings")
        email_layout = QGridLayout()
        
        # Sender details
        self.sender_address_input = QLineEdit()
        email_layout.addWidget(QLabel('Sender Address:'), 0, 0)
        email_layout.addWidget(self.sender_address_input, 0, 1)
        
        self.sender_name_input = QLineEdit()
        email_layout.addWidget(QLabel('Sender Name:'), 1, 0)
        email_layout.addWidget(self.sender_name_input, 1, 1)
        
        # Email headers
        self.reply_to_input = QLineEdit()
        email_layout.addWidget(QLabel('Reply To:'), 2, 0)
        email_layout.addWidget(self.reply_to_input, 2, 1)
        
        self.cc_input = QLineEdit()
        email_layout.addWidget(QLabel('CC:'), 3, 0)
        email_layout.addWidget(self.cc_input, 3, 1)
        
        self.bcc_input = QLineEdit()
        email_layout.addWidget(QLabel('BCC:'), 4, 0)
        email_layout.addWidget(self.bcc_input, 4, 1)
        
        # Subject and body
        self.subject_input = QLineEdit()
        email_layout.addWidget(QLabel('Subject:'), 5, 0)
        email_layout.addWidget(self.subject_input, 5, 1)
        
        # Body format selection
        format_layout = QHBoxLayout()
        self.plain_text_radio = QRadioButton('Plain Text')
        self.html_radio = QRadioButton('HTML')
        self.html_radio.setChecked(True)
        format_layout.addWidget(self.plain_text_radio)
        format_layout.addWidget(self.html_radio)
        
        email_layout.addWidget(QLabel('Format:'), 6, 0)
        email_layout.addLayout(format_layout, 6, 1)
        
        self.body_input = QTextEdit()
        email_layout.addWidget(QLabel('Body:'), 7, 0)
        email_layout.addWidget(self.body_input, 7, 1)
        
        # Attachment
        attachment_layout = QHBoxLayout()
        self.attachment_input = QLineEdit()
        self.attachment_browse_button = QPushButton('Browse')
        attachment_layout.addWidget(self.attachment_input)
        attachment_layout.addWidget(self.attachment_browse_button)
        
        email_layout.addWidget(QLabel('Attachment:'), 8, 0)
        email_layout.addLayout(attachment_layout, 8, 1)
        
        email_group.setLayout(email_layout)

        left_layout.addWidget(smtp_group)
        left_layout.addWidget(email_group)

        # Right section (Control Panel)
        right_layout = QVBoxLayout()
        control_group = QGroupBox("Control Panel")
        control_layout = QVBoxLayout()
        
        # Settings
        settings_form = QFormLayout()
        self.emails_per_smtp_input = QSpinBox()
        self.emails_per_smtp_input.setRange(1, 10000)
        self.emails_per_smtp_input.setValue(1000)
        settings_form.addRow('Emails per SMTP:', self.emails_per_smtp_input)
        
        self.delivery_options_button = QPushButton('Delivery Options')
        settings_form.addRow(self.delivery_options_button)
        
        control_layout.addLayout(settings_form)
        
        # Status
        self.status_label = QLabel('Status: Ready')
        self.status_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.progress_bar)
        
        # Control buttons
        button_layout = QGridLayout()
        self.start_button = QPushButton('Start')
        self.pause_button = QPushButton('Pause')
        self.resume_button = QPushButton('Resume')
        self.stop_button = QPushButton('Stop')
        
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button, 0, 0)
        button_layout.addWidget(self.pause_button, 0, 1)
        button_layout.addWidget(self.resume_button, 1, 0)
        button_layout.addWidget(self.stop_button, 1, 1)
        
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        
        right_layout.addWidget(control_group)
        right_layout.addStretch()

        # Add left and right layouts to horizontal layout
        h_layout.addLayout(left_layout, 2)
        h_layout.addLayout(right_layout, 1)

        main_layout.addLayout(h_layout)
        self.tabs.addTab(main_tab, "Main")

    def setup_email_list_tab(self):
        """Set up the email list tab."""
        email_list_tab = QWidget()
        layout = QVBoxLayout(email_list_tab)
        
        # Email list input
        self.email_input = QTextEdit()
        self.email_input.setPlaceholderText("Enter email addresses (one per line)")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.load_email_button = QPushButton('Load from File')
        self.validate_email_button = QPushButton('Validate Emails')
        button_layout.addWidget(self.load_email_button)
        button_layout.addWidget(self.validate_email_button)
        
        layout.addWidget(QLabel('Email List:'))
        layout.addWidget(self.email_input)
        layout.addLayout(button_layout)
        
        self.tabs.addTab(email_list_tab, "Email List")

    def setup_log_tab(self):
        """Set up the log tab."""
        log_tab = QWidget()
        layout = QVBoxLayout(log_tab)
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        
        layout.addWidget(self.log_text)
        
        self.tabs.addTab(log_tab, "Log")

    def setup_proxy_tab(self):
        """Set up the proxy settings tab."""
        proxy_tab = QWidget()
        layout = QVBoxLayout(proxy_tab)
        
        self.use_proxy_checkbox = QCheckBox("Use Proxies")
        layout.addWidget(self.use_proxy_checkbox)
        
        self.proxy_input = QTextEdit()
        self.proxy_input.setPlaceholderText("Enter proxies (one per line)\nFormat: host:port")
        
        layout.addWidget(QLabel('Proxy List:'))
        layout.addWidget(self.proxy_input)
        
        self.tabs.addTab(proxy_tab, "Proxy Settings")

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
        # TODO: Implement settings save functionality
        pass

    def load_settings(self):
        """Load settings from a file."""
        # TODO: Implement settings load functionality
        pass

    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About DigitalGuards Mailer",
            "DigitalGuards Mailer v1.0\n\n"
            "A professional email marketing tool.\n\n"
            "© 2024 DigitalGuards"
        )
