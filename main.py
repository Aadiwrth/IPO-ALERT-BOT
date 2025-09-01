import os
import threading
import httpx
from datetime import datetime
from dotenv import load_dotenv

# ===== LOAD ENV =====
load_dotenv()

API_KEY = os.getenv("BREVO_API_KEY")
FROM_NAME = os.getenv("FROM_NAME")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
ONGOING_URL = os.getenv("ONGOING_URL")
TOTAL_APPS = int(os.getenv("TOTAL_APPS", 2500000))


# ===== EMAIL SENDER VIA BREVO (THREAD SAFE) =====
def send_email(email, subject, content):
    try:
        res = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
                "to": [{"email": email}],
                "subject": subject,
                "textContent": content
            },
            timeout=10
        )
        if res.status_code != 201:
            print(f"[❌] Failed to send email to {email}: {res.text}")
        else:
            print(f"[✅] Email sent to {email}")
    except Exception as e:
        print(f"[⚠️] Error sending email to {email}: {e}")


def send(email, subject, content):
    threading.Thread(target=send_email, args=(email, subject, content)).start()


# ===== MAIN LOGIC =====
def main():
    today_str = datetime.now().strftime("%Y-%m-%d")

    with httpx.Client() as client:
        resp = client.get(ONGOING_URL)
        resp.raise_for_status()
        data = resp.json()

    for ipo in data["response"]:
        open_date = ipo["open_date"].split(" ")[0] if ipo["open_date"] else None
        close_date = ipo["close_date"].split(" ")[0] if ipo["close_date"] else None

        if open_date == today_str:
            # calc remaining days
            rem_days = (datetime.strptime(close_date, "%Y-%m-%d") - datetime.now()).days

            # probability rough estimate
            prob = (ipo["shares_offered"] / TOTAL_APPS) * 100
            sug_qty = 10 if prob < 90 else "more than 10"
            suggestion = (
                "Only 10 units can be allotted due to oversubscription."
                if prob < 90
                else "You can apply for more than 10 units due to high probability."
            )
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <!-- Logo instead of multiple breaks -->
        <div style="text-align:center; margin-bottom:20px;">
            <img src="https://meroshare.cdsc.com.np/assets/img/brand-login.png" 
                alt="Meroshare Logo" width="200" style="display:block; margin:auto;">
        </div>

        <h2 style="color:#2e86c1;">
            <img data-emoji="🚀" class="an1" alt="🚀" aria-label="🚀" draggable="false" 
                src="https://fonts.gstatic.com/s/e/notoemoji/16.0/1f680/72.png" loading="lazy"> 
            IPO Alert: {ipo['company_name']} is now OPEN!
        </h2>

        <p style="font-size:16px;">Get ready to invest! Here's the important info:</p>

        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td style="padding:8px;font-weight:bold">Scrip:</td><td style="padding:8px">{ipo['finid']}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Company Name:</td><td style="padding:8px">{ipo['company_name']}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Remaining Days:</td><td style="padding:8px">{rem_days} day(s) remaining</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Issue Date:</td><td style="padding:8px">{open_date}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Issue Close Date:</td><td style="padding:8px">{close_date}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Total Units:</td><td style="padding:8px">{ipo['shares_offered']:,}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Probability of Allotment:</td><td style="padding:8px">{prob:.2f}%</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Suggested Quantity:</td><td style="padding:8px">{sug_qty}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Suggestion:</td><td style="padding:8px">{suggestion}</td></tr>
        </table>

        <p style="margin-top:20px; font-size:14px; color:#555;">
            <img data-emoji="⚠️" class="an1" alt="⚠️" aria-label="⚠️" draggable="false" 
                src="https://fonts.gstatic.com/s/e/notoemoji/16.0/26a0_fe0f/72.png" loading="lazy"> 
            If this email landed in your spam folder, please mark it as <strong>Not Spam</strong> to get future alerts.
        </p>

        <p style="font-size:12px; color:#777;">
            <img data-emoji="ℹ️" class="an1" alt="ℹ️" aria-label="ℹ️" draggable="false" 
                src="https://fonts.gstatic.com/s/e/notoemoji/16.0/2139_fe0f/72.png" loading="lazy"> 
            The number of total applications is assumed as {TOTAL_APPS:,} for probability calculation.
        </p>
    </body>
    </html>
    """


    subject = f"🚀 IPO Alert: {ipo['company_name']} is now OPEN!"
    send(TO_EMAIL, subject, body)

if __name__ == "__main__":
    main()
