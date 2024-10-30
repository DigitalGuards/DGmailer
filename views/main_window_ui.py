from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QTextEdit, QPushButton,
                            QProgressBar, QFileDialog, QMessageBox, QCheckBox,
                            QSpinBox, QTabWidget, QGroupBox, QGridLayout,
                            QPlainTextEdit, QMenuBar, QMenu, QAction,
                            QButtonGroup, QRadioButton, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

class MainWindowUI(QMainWindow):
    """UI setup for the main window of the email sender application."""

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
