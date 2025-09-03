# IPO Alert Bot

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/yourusername/ipo-alert-bot/graphs/commit-activity)

A professional, modular IPO monitoring system that automatically tracks Initial Public Offering (IPO) openings and delivers real-time notifications via email and Discord. Built for reliability and continuous operation with comprehensive error handling and dynamic configuration updates.

## 🚀 Features

### Core Functionality
- **🔄 Automated IPO Monitoring**: Continuously tracks ongoing IPOs and detects new openings
- **📧 Multi-Channel Notifications**: Professional HTML email alerts and Discord rich embeds
- **📊 Investment Analysis**: Calculates allotment probability and provides investment recommendations
- **⏰ Real-Time Alerts**: Instant notifications when IPOs open for subscription
- **🌏 Nepal Time Support**: Optimized for Nepal Stock Exchange (NEPSE) timezone

### Advanced Features  
- **🔥 Hot Reload**: Dynamic email list updates without bot restart using file monitoring
- **💾 Duplicate Prevention**: Intelligent tracking prevents duplicate alerts per day
- **🛡️ Robust Error Handling**: Comprehensive error recovery and admin notifications
- **📈 Professional Templates**: Beautifully designed HTML email templates with investment metrics
- **🤖 Discord Integration**: Rich embed notifications with probability indicators and urgency levels
- **📋 Comprehensive Logging**: Detailed logging to both console and file for monitoring and debugging

### System Reliability
- **⚡ Connection Testing**: Pre-flight checks for all external services
- **🔄 Auto-Recovery**: Continues operation even when individual services fail
- **📱 Admin Notifications**: Real-time system status updates via email and Discord
- **📊 Monitoring**: Built-in health checks and performance tracking

## 🏗️ Architecture

The application follows a modular, service-oriented architecture for maximum maintainability and extensibility:

```
ipo_alert_bot/
├── 🎯 main.py                    # Application orchestrator
├── ⚙️  config.py                  # Centralized configuration
├── 🛠️  utils.py                   # Shared utilities
├── 🌐 api_service.py             # External API integration
├── 📧 email_service.py           # Email delivery service
├── 🎨 email_templates.py         # HTML template engine
├── 🤖 discord_integration.py     # Discord bot service  
├── 👁️  file_watcher.py           # Real-time file monitoring
├── 🔄 ipo_processor.py          # Core business logic
├── 🔍 test_service.py           # Health check utilities
└── 📋 requirements.txt          # Dependencies
```

## 🛠️ Requirements

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 256MB RAM
- **Storage**: 100MB free space for logs and data
- **Network**: Stable internet connection for API calls

### External Services
- **Email Provider**: [Brevo](https://www.brevo.com/) SMTP API account
- **Discord Bot**: Optional Discord application with bot token
- **IPO Data API**: Access to IPO data endpoint

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/Aadiwrth/IPO-ALERT-BOT.git
cd IPO-ALERT-BOT
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root:

```env
# === EMAIL CONFIGURATION ===
BREVO_API_KEY=your_brevo_api_key_here
FROM_NAME=IPO Alert System
FROM_EMAIL=alerts@yourdomain.com
TO_EMAIL=admin@yourdomain.com

# === IPO DATA API ===
ONGOING_URL=https://api.yourprovider.com/v1/ongoing-ipos

# === BOT SETTINGS ===
TOTAL_APPS=2500000              # Estimated total applications for probability calculation
CHECK_INTERVAL_HOURS=5          # How often to check for new IPOs

# === DISCORD INTEGRATION (Optional) ===
DISCORD_TOKEN=your_discord_bot_token
# DISCORD_GUILD_ID and DISCORD_CHANNEL_ID are set in config.py
```

### 5. Set Up Email Subscribers
Create `email_update.txt` with subscriber emails (one per line):

```txt
# IPO Alert Subscribers
# Lines starting with # are comments and will be ignored

investor1@example.com
investor2@example.com
portfolio.manager@company.com

# You can add comments anywhere
trader@investment.firm

# The bot monitors this file for changes in real-time
```

## 🚀 Usage

### Starting the Bot
```bash
python __run__.py
```

### What Happens Next
1. **🔍 System Check**: Validates configuration and tests all connections
2. **🚀 Initialization**: Starts Discord bot and file monitoring services  
3. **📧 Startup Notification**: Sends confirmation to admin email and Discord
4. **🔄 Monitoring Loop**: Begins continuous IPO monitoring cycle
5. **📊 Alert Processing**: Detects IPO openings and sends notifications
6. **💤 Sleep Cycle**: Waits for next check interval

### Real-Time Operations
- **📝 Email List Updates**: Modify `email_update.txt` anytime - changes apply immediately
- **📊 Monitoring**: Watch logs in real-time: `tail -f ipo_bot.log`
- **🛑 Graceful Shutdown**: Use `Ctrl+C` for clean shutdown with proper cleanup

## 📧 Notification Templates

### Email Alerts
Professional HTML emails featuring:
- **Company Information**: Name, symbol, sector, issue manager
- **Financial Details**: Offer price, total shares, timeline
- **Investment Analysis**: Probability calculation and recommendations
- **Responsive Design**: Optimized for desktop and mobile viewing

### Discord Notifications
Rich embed messages including:
- **Color-coded Priority**: Green (high probability), Orange (medium), Red (low)
- **Comprehensive Metrics**: All key IPO information in organized fields
- **Action Buttons**: Direct links to broker platforms (customizable)
- **Urgency Indicators**: Special alerts for limited-time opportunities

## 📊 Investment Analysis Engine

The bot provides sophisticated investment guidance:

### Probability Calculation
```
Allotment Probability = (Total IPO Shares ÷ Estimated Applications) × 100
```

### Recommendation Logic
- **High Probability (≥50%)**: Suggests higher allocation quantities
- **Medium Probability (20-49%)**: Balanced approach with standard quantities
- **Low Probability (<20%)**: Conservative strategy with minimum allocation

### Risk Assessment
- **Timeline Analysis**: Considers days remaining for subscription
- **Market Conditions**: Factors in historical oversubscription rates
- **Strategic Recommendations**: Tailored advice based on probability metrics

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BREVO_API_KEY` | Brevo SMTP API key | - | ✅ |
| `FROM_NAME` | Sender display name | IPO Alert System | ✅ |
| `FROM_EMAIL` | Sender email address | - | ✅ |
| `TO_EMAIL` | Admin email for notifications | - | ✅ |
| `ONGOING_URL` | IPO data API endpoint | - | ✅ |
| `TOTAL_APPS` | Estimated total applications | 2500000 | ❌ |
| `CHECK_INTERVAL_HOURS` | Check frequency in hours | 5 | ❌ |
| `DISCORD_TOKEN` | Discord bot token | - | ❌ |

### Customization Options

#### Email Templates (`email_templates.py`)
```python
def create_ipo_alert_email(ipo, rem_days, prob, sug_qty, suggestion):
    # Customize HTML template, colors, styling
    # Add company logos, charts, additional metrics
    return html_content
```

#### Discord Embeds (`discord_integration.py`)
```python
async def create_ipo_embed(self, ipo, rem_days, prob, sug_qty, suggestion):
    # Modify embed fields, colors, thumbnails
    # Add interactive buttons, custom formatting
    return embed
```

## 📈 Monitoring & Logging

### Log Levels
- **INFO**: Normal operations, successful alerts, system status
- **WARNING**: Non-critical issues, missing data, service degradation  
- **ERROR**: Failed operations, API errors, connection issues
- **DEBUG**: Detailed execution information (enable in development)

### Log Locations
- **Console Output**: Real-time monitoring during development
- **File Logging**: Persistent logs in `ipo_bot.log` with rotation
- **System Notifications**: Critical alerts sent to admin via email/Discord

### Performance Metrics
The bot automatically tracks:
- **API Response Times**: Monitor external service performance
- **Email Delivery Rates**: Track successful notification delivery
- **Error Frequencies**: Identify and resolve recurring issues
- **System Uptime**: Monitor continuous operation reliability

## 🔒 Security Considerations

### API Key Management
- Store sensitive credentials in `.env` file only
- Never commit API keys to version control
- Use environment-specific configurations for different deployments
- Regularly rotate API keys and tokens

### Email Security
- Validate email addresses before sending
- Implement rate limiting to prevent spam
- Use secure SMTP connections (TLS/SSL)
- Monitor for bounce rates and blacklisting

### Error Information
- Sanitize error messages in notifications
- Avoid exposing internal system information
- Log detailed errors locally, send summaries to admin
- Implement secure error reporting channels

## 🚀 Deployment Options

### Local Development
```bash
# Development with debug logging
export DEBUG=true
python __run__.py
```

### Production Server
```bash
# Background process with log output
nohup python __run__.py > bot_output.log 2>&1 &
```

### Docker Container (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "__run__.py"]
```

### System Service (Linux)
```ini
# /etc/systemd/system/ipo-alert-bot.service
[Unit]
Description=IPO Alert Bot
After=network.target

[Service]
Type=simple
User=ipo-bot
WorkingDirectory=/opt/ipo-alert-bot
ExecStart=/usr/bin/python3 __run__.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🧪 Testing

### Connection Testing
The bot includes built-in connection testing:
```bash
python -c "from test_service import test_all_connections; test_all_connections()"
```

### Manual Testing
```bash
# Test email functionality
python -c "from email_service import send_email; from email_templates import create_system_notification_email; send_email('test@example.com', 'Test', create_system_notification_email('Test', 'Test message'))"

# Test API connectivity  
python -c "from api_service import fetch_ipo_data; print(len(fetch_ipo_data()), 'IPOs found')"
```

### Development Testing
- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Verify service interactions
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Monitor resource usage and response times

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

### Development Setup
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Install** development dependencies: `pip install -r requirements-dev.txt`
4. **Make** your changes with comprehensive tests
5. **Test** thoroughly across different scenarios
6. **Commit** with descriptive messages: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Create** a Pull Request with detailed description

### Contribution Guidelines
- **Code Style**: Follow PEP 8 with 88-character line limit
- **Documentation**: Update README and inline comments for new features
- **Testing**: Include unit tests for new functionality
- **Backwards Compatibility**: Maintain compatibility with existing configurations
- **Performance**: Consider impact on system resources and API rate limits

### Priority Areas
- 🔌 **New Integrations**: Additional notification channels (Slack, Telegram, SMS)
- 📊 **Enhanced Analytics**: Advanced probability models and market analysis
- 🎨 **UI Improvements**: Web dashboard for configuration and monitoring
- 🔍 **Data Sources**: Integration with multiple IPO data providers
- 📱 **Mobile Support**: Native mobile applications for alerts

## 🙏 Acknowledgments

- **Brevo**: Reliable email delivery service
- **Discord.py**: Excellent Discord API wrapper
- **Python Community**: Outstanding libraries and documentation
- **Contributors**: Everyone who helps improve this project

## 📞 Support

### Getting Help
- **📖 Documentation**: Comprehensive guides in this README
- **🐛 Issues**: Report bugs via [GitHub Issues](https://github.com/Aadiwrth/IPO-ALERT-BOT/issues)
- **💬 Discussions**: Join the Community support in [Discord Community](https://discord.gg/MNDxjacF)


### Quick Troubleshooting
- **Connection Errors**: Verify API keys and network connectivity
- **Email Issues**: Check Brevo account status and sending limits
- **Discord Problems**: Ensure bot has proper permissions in target server
- **File Monitoring**: Confirm `email_update.txt` exists and is readable

---

<div align="center">

**Built with ❤️ for the investing community**

[⭐ Star this project](https://github.com/Aadiwrth/IPO-ALERT-BOT) | [🍴 Fork it](https://github.com/Aadiwrth/IPO-ALERT-BOT/fork) | [📥 Download](https://github.com/Aadiwrth/IPO-ALERT-BOT/archive/refs/heads/main.zip)




# Buy me a Coffee ☕:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/wokuu)
[![Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://patreon.com/wokuu)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/deepu468)
</div>