
# IPO Alert Bot

Automated bot to monitor ongoing IPOs and send email alerts to subscribers. Built with Python, the bot fetches IPO data, calculates probability of allotment, and sends professional HTML email notifications. Designed for continuous operation with dynamic email list updates.

---

## Features

- ✅ **Automated IPO Monitoring:** Continuously fetches ongoing IPO data and checks for new openings.  
- ✅ **Email Alerts:** Sends professional HTML email notifications using the Brevo SMTP API.  
- ✅ **Probability Analysis:** Calculates allotment probability and recommended quantity based on total applications.  
- ✅ **Dynamic Email List:** Watches `email_update.txt` for updates without restarting the bot.  
- ✅ **System Notifications:** Sends startup, error, and test notifications to the admin.  
- ✅ **Timezone Support:** Operates in Nepal Time (NPT).  
- ✅ **Logging:** Full log tracking with console and file logging.  

---

## Requirements

- Python 3.10+  
- Packages:
  ```bash
  pip install httpx python-dotenv pytz watchdog
  ```

* A `.env` file with the following variables:

```env
BREVO_API_KEY=your_brevo_api_key
FROM_NAME=Your Name
FROM_EMAIL=your_email@example.com
TO_EMAIL=admin_email@example.com
ONGOING_URL=https://api.example.com/ongoing-ipos
TOTAL_APPS=2500000          # Total estimated applications for probability calculation
CHECK_INTERVAL_HOURS=5      # Frequency of checks
```

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ipo-alert-bot.git
cd ipo-alert-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file with your configuration (see Requirements).

4. Add subscriber emails in `email_update.txt` (one email per line). Lines starting with `#` are ignored.

---

## Usage

Run the bot:

```bash
python main.py
```

* The bot will monitor IPO openings every `CHECK_INTERVAL_HOURS`.
* Sends alerts to all valid emails in `email_update.txt`.
* Automatically tracks sent emails per day to avoid duplicates.
* Logs all activity to `ipo_bot.log`.

**Testing connections**:
Before running continuously, the bot tests API connectivity and email sending to the admin.

---

## Email Template

![alt text](/assets/image.png)
---

## File Structure

```
.
├── main.py                # Main bot script
├── email_update.txt       # Subscriber emails
├── ipo_bot.log            # Log file
├── .env                   # Environment configuration
└── README.md              # Project documentation
```

---

## Logging

* Logs both to console and `ipo_bot.log`.
* Includes info, warnings, and errors.
* Tracks sent emails, API fetch results, and system notifications.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request
5. I'll happily appreciate any small effort put into this project :)

---
