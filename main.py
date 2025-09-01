import os
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


# ===== EMAIL SENDER VIA BREVO =====
def send_email(subject: str, body: str, to_email: str = TO_EMAIL):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY,
    }
    payload = {
        "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }
    with httpx.Client() as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print("✅ Email sent:", r.json())


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
            rem_days = (
                datetime.strptime(close_date, "%Y-%m-%d") - datetime.now()
            ).days

            # probability rough estimate
            prob = (ipo["shares_offered"] / TOTAL_APPS) * 100
            sug_qty = 10 if prob < 90 else "more than 10"
            suggestion = (
                "Only 10 units can be allotted due to oversubscription."
                if prob < 90
                else "You can apply for more than 10 units due to high probability."
            )

            body = f"""
IPO Alert: {ipo['company_name']} IPO is now open!

Scrip: {ipo['finid']}
Company Name: {ipo['company_name']}
Remaining Days: {rem_days} days remaining
Issue Date: {open_date}
Issue Close Date: {close_date}
Total Units: {ipo['shares_offered']:,}
Probability of Allotment: {prob:.2f}%
Suggested Quantity: {sug_qty}
Suggestion: {suggestion}

If you find this email in your spam folder, please mark it as 'Not Spam' to receive future emails in your inbox.

The number of total applications is assumed as {TOTAL_APPS:,} for probability calculation.
"""
            subject = f"IPO Alert: {ipo['company_name']} IPO is now open!"
            send_email(subject, body)


if __name__ == "__main__":
    main()
