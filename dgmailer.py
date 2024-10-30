import sys
from PyQt5.QtWidgets import QApplication
import views.resources_rc  # Import resources before MainWindow
from views.main_window import MainWindow

def main():
    """Main entry point of the application."""
    app = QApplication(sys.argv)
    
    # Set application-wide attributes
    app.setApplicationName("DigitalGuards Mailer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("DigitalGuards")
    app.setOrganizationDomain("digitalguards.nl")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
