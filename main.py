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
                "htmlContent": content  # Changed to htmlContent for proper HTML rendering
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
                "Conservative approach recommended due to high demand."
                if prob < 90
                else "Higher allocation possible due to favorable probability."
            )

            body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPO Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8f9fa;">
    
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px;">
                IPO Opening Alert
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                Investment Opportunity Notification
            </p>
        </div>

        <!-- Main Content -->
        <div style="padding: 40px;">
            
            <!-- Company Alert -->
            <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0;">
                <h2 style="color: #1976d2; margin: 0 0 8px 0; font-size: 20px; font-weight: 600;">
                    {ipo['company_name']}
                </h2>
                <p style="color: #424242; margin: 0; font-size: 14px;">
                    IPO is now open for subscription
                </p>
            </div>

            <!-- IPO Details -->
            <div style="margin-bottom: 30px;">
                <h3 style="color: #333; margin: 0 0 20px 0; font-size: 18px; font-weight: 600; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">
                    Issue Details
                </h3>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; width: 40%; border-bottom: 1px solid #f5f5f5;">
                            Company
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['company_name']}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Symbol
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['finid']}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Opening Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {open_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Closing Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {close_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Days Remaining
                        </td>
                        <td style="padding: 12px 0; color: #e65100; font-weight: 700; border-bottom: 1px solid #f5f5f5;">
                            {rem_days} day{'s' if rem_days != 1 else ''}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Total Shares
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['shares_offered']:,}
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Investment Analysis -->
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #333; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                    Investment Analysis
                </h3>
                
                <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                    <div style="flex: 1; min-width: 200px;">
                        <p style="margin: 0 0 8px 0; color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                            Allotment Probability
                        </p>
                        <p style="margin: 0; font-size: 24px; font-weight: 700; color: {'#4caf50' if prob >= 50 else '#ff9800' if prob >= 20 else '#f44336'};">
                            {prob:.1f}%
                        </p>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <p style="margin: 0 0 8px 0; color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                            Recommended Quantity
                        </p>
                        <p style="margin: 0; font-size: 24px; font-weight: 700; color: #333;">
                            {sug_qty} units
                        </p>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #ffffff; border-radius: 6px; border-left: 3px solid #2196f3;">
                    <p style="margin: 0; color: #555; font-size: 14px; line-height: 1.5;">
                        <strong>Recommendation:</strong> {suggestion}
                    </p>
                </div>
            </div>

        </div>

        <!-- Footer -->
        <div style="background-color: #f5f5f5; padding: 25px 40px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                This analysis is based on estimated total applications of {TOTAL_APPS:,}
            </p>
            <p style="margin: 0; color: #999; font-size: 11px;">
                Please ensure this email is marked as "Not Spam" to receive future notifications
            </p>
        </div>

    </div>
</body>
</html>
"""

            subject = f"IPO Alert: {ipo['company_name']} Now Open"
            send(TO_EMAIL, subject, body)

if __name__ == "__main__":
    main()