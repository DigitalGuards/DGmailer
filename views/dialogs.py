from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QSpinBox, QComboBox, QDialogButtonBox,
                            QLabel)
from PyQt5.QtCore import Qt
from models.smtp_server import SMTPServer

class AddSMTPDialog(QDialog):
    """Dialog for adding a new SMTP server."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add SMTP Server')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Server details
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText('smtp.example.com')
        form_layout.addRow('Server:', self.server_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(587)
        form_layout.addRow('Port:', self.port_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('username@example.com')
        form_layout.addRow('Username:', self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Password:', self.password_input)

        self.tls_mode_input = QComboBox()
        self.tls_mode_input.addItems([
            "ON / Auto",
            "ON / Explicit TLS",
            "ON / Implicit TLS",
            "OFF"
        ])
        form_layout.addRow('TLS Mode:', self.tls_mode_input)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_smtp_server(self) -> SMTPServer:
        """Get the SMTP server details from the dialog.

        Returns:
            SMTPServer: The SMTP server configuration
        """
        return SMTPServer(
            server=self.server_input.text(),
            port=self.port_input.value(),
            username=self.username_input.text(),
            password=self.password_input.text(),
            tls_mode=self.tls_mode_input.currentText()
        )

class DeliveryOptionsDialog(QDialog):
    """Dialog for configuring email delivery options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Delivery Options')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Delivery settings
        self.frequency_input = QSpinBox()
        self.frequency_input.setRange(1, 3600)
        self.frequency_input.setValue(1)
        self.frequency_input.setSuffix(' seconds')
        form_layout.addRow('Frequency:', self.frequency_input)

        self.daily_limit_input = QSpinBox()
        self.daily_limit_input.setRange(0, 1000000)
        self.daily_limit_input.setValue(0)
        self.daily_limit_input.setSpecialValueText('No limit')
        form_layout.addRow('Daily Limit:', self.daily_limit_input)

        self.hourly_limit_input = QSpinBox()
        self.hourly_limit_input.setRange(0, 100000)
        self.hourly_limit_input.setValue(0)
        self.hourly_limit_input.setSpecialValueText('No limit')
        form_layout.addRow('Hourly Limit:', self.hourly_limit_input)

        # Help text
        help_text = QLabel(
            "Set to 0 for no limit. Be careful with email frequency to avoid "
            "being marked as spam."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: gray; font-size: 11px;")

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(help_text)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_delivery_options(self) -> dict:
        """Get the delivery options from the dialog.

        Returns:
            dict: The delivery options configuration
        """
        return {
            'frequency': self.frequency_input.value(),
            'daily_limit': self.daily_limit_input.value(),
            'hourly_limit': self.hourly_limit_input.value()
        }
