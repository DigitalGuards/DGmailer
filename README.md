# DigitalGuards Mailer

![DigitalGuards Mailer](https://github.com/user-attachments/assets/1add7b7a-0544-40d8-aff7-417a3af63f82)

A professional email marketing tool built with Python and PyQt5. DigitalGuards Mailer provides a robust and user-friendly interface for managing email campaigns with support for multiple SMTP servers, optional proxy support, and advanced delivery controls.

## Features

### 🚀 Core Features
- **Multiple SMTP Support**: Configure and rotate between multiple SMTP servers
- **Optional Proxy Support**: Additional layer of connection privacy if needed (not required for standard email operations)
- **Rate Limiting**: Configurable daily and hourly sending limits
- **Email Customization**: 
  - HTML/Plain Text support
  - Custom sender name and reply-to addresses
  - CC/BCC functionality
  - File attachments
- **Bulk Email Management**: Import recipient lists from TXT, CSV, or Excel files

### 🔄 Intelligent SMTP Rotation System

The application implements a smart SMTP server rotation system that helps maintain high deliverability rates and optimal email sending performance:

#### Automatic Load Balancing
- **Configurable Email Limits**: Set maximum emails per SMTP server
- **Smart Rotation**: Automatically switches servers based on usage
- **Health-Based Selection**: Prioritizes healthy, performing servers
- **Automatic Failover**: Switches to backup servers when needed

#### Health Monitoring
- **Error Tracking**:
  * Monitors consecutive failures
  * Tracks error rates per server
  * Records performance metrics
- **Automatic Recovery**:
  * 15-minute cooldown for problematic servers
  * Automatic server recovery after cooldown
  * Smart fallback to best-performing servers

#### Performance Optimization
- **Usage Statistics**:
  * Tracks emails sent per server
  * Monitors success rates
  * Records response times
- **Adaptive Routing**:
  * Automatically adjusts to server performance
  * Balances load across available servers
  * Optimizes delivery success rates

### 💎 Advanced Features
- **Smart Queue Management**: 
  - Intelligent SMTP rotation
  - Configurable emails per server
  - Built-in delay controls
- **Progress Tracking**: 
  - Real-time sending progress
  - Detailed logging
  - Status updates
- **Error Handling**: 
  - SMTP connection testing
  - Delivery status tracking
  - Comprehensive error reporting

### 🎨 User Interface
- **Modern Design**: Clean and intuitive interface
- **Theme Support**: Switch between light and dark themes
- **Responsive Layout**: Adapts to different window sizes
- **Tab Organization**: 
  - Main sending controls
  - Email list management
  - Proxy settings (optional)
  - Live logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/digitalguards/dgmailer.git
cd dgmailer
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv mailer
source mailer/bin/activate  # On Windows: mailer\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python dgmailer.py
```

## Usage

### Setting Up SMTP Servers

1. Click "Add SMTP Server" in the main tab
2. Enter your SMTP server details:
   - Server address
   - Port
   - Username
   - Password
   - TLS mode
3. Test the connection using the "Test" button

### Configuring Email Settings

1. Fill in the email details:
   - Sender address
   - Sender name (optional)
   - Reply-to address (optional)
   - CC/BCC recipients (optional)
2. Enter your email subject and body
3. Choose between HTML or plain text format
4. Add attachments if needed

### Managing Recipients

1. Navigate to the "Email List" tab
2. Either:
   - Enter email addresses manually (one per line)
   - Click "Load from File" to import from TXT/CSV/Excel
3. Use "Validate Emails" to check the format of addresses

### Configuring SMTP Rotation

1. Add multiple SMTP servers through the UI
2. Set "Emails per SMTP" value in the control panel
3. The system will automatically:
   - Rotate servers based on the email limit
   - Monitor server health and errors
   - Apply cooldown periods when needed
   - Select the best performing servers

### Optional Proxy Configuration

While not required for standard email operations (as SMTP servers handle the actual email sending), proxies can be used if additional connection privacy is needed:

1. Go to the "Proxy Settings" tab
2. Enable "Use Proxies"
3. Enter proxy servers (one per line) in host:port format

Note: Proxies only affect the connection between your client and the SMTP server. They do not impact the actual email delivery or the IP address that recipients see (which will be your SMTP server's IP).

### Delivery Controls

1. Click "Delivery Options" to configure:
   - Sending frequency
   - Daily limits
   - Hourly limits
2. Set emails per SMTP server in the main control panel

### Starting the Campaign

1. Review all settings
2. Click "Start" to begin sending
3. Use Pause/Resume/Stop controls as needed
4. Monitor progress in the status bar and log tab

### Monitoring

The system provides detailed monitoring through:
1. Real-time status updates
2. Progress bar showing overall completion
3. Detailed logs showing:
   - Email delivery status
   - SMTP server rotations
   - Error messages
   - Performance metrics

## Best Practices for Email Deliverability

To maintain high deliverability rates:

1. **SMTP Server Configuration**:
   - Use reputable SMTP providers
   - Configure proper SPF, DKIM, and DMARC records
   - Monitor server reputation

2. **Email Content**:
   - Use proper HTML formatting
   - Include text alternatives
   - Follow anti-spam guidelines

3. **Sending Patterns**:
   - Use appropriate rate limits
   - Implement gradual sending increases
   - Monitor bounce rates

4. **List Management**:
   - Keep lists clean and updated
   - Remove bounced addresses
   - Honor unsubscribe requests

## Screenshots

### Light Theme
![Light Theme](screenshots/light.png)

### Dark Theme
![Dark Theme](screenshots/dark.png)

### SMTP Configuration
![SMTP Setup](screenshots/smtp.png)

### Email List Management
![Email List](screenshots/email-list.png)

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/AmazingFeature
```
3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```
4. Make your changes
5. Run tests:
```bash
python -m pytest
```
6. Commit your changes:
```bash
git commit -m 'Add some AmazingFeature'
```
7. Push to the branch:
```bash
git push origin feature/AmazingFeature
```
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Email handling via [smtplib](https://docs.python.org/3/library/smtplib.html)
- Proxy support using [PySocks](https://github.com/Anorov/PySocks)
- Data handling with [pandas](https://pandas.pydata.org/)

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/digitalguards/dgmailer/issues) page
2. Create a new issue if your problem isn't already listed
3. Visit our [website](https://digitalguards.nl) for more information
4. Contact us at support@digitalguards.nl

---

Made with ❤️ by [DigitalGuards](https://digitalguards.nl)
