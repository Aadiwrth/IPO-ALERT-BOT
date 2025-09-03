from ..config import TOTAL_APPS
from ..utils import get_nepal_time


def create_ipo_alert_email(ipo, rem_days, prob, sug_qty, suggestion):
    """Create professional HTML email body for IPO alerts"""
    return f"""
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
                            Sector
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo.get('Sector', 'N/A')}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Offer Price
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            NPR {ipo.get('offer_price', 'N/A')}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Opening Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['open_date'].split(' ')[0]}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Closing Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['close_date'].split(' ')[0]}
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
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500;">
                            Issue Manager
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600;">
                            {ipo.get('issue_manager', 'N/A')}
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

            <!-- Action Note -->
            <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; border-left: 3px solid #ff9800;">
                <p style="margin: 0; color: #e65100; font-size: 14px; font-weight: 500;">
                    <strong>Action Required:</strong> IPO subscription window is now open. Please review and submit your application through your broker.
                </p>
            </div>

        </div>

        <!-- Footer -->
        <div style="background-color: #f5f5f5; padding: 25px 40px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                This analysis is based on estimated total applications of {TOTAL_APPS:,}
            </p>
            <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                Automated IPO Alert System • Last checked: {get_nepal_time().strftime('%Y-%m-%d %H:%M:%S')} NPT
            </p>
            <p style="margin: 0; color: #999; font-size: 11px;">
                You received this because you're subscribed to IPO alerts
            </p>
        </div>

    </div>
</body>
</html>
"""


def create_system_notification_email(title, message, status_type="info"):
    """Create HTML body for system notifications (startup, test, error)"""
    color_map = {
        "success": {"bg": "#e8f5e8", "border": "#4caf50", "text": "#2e7d32"},
        "info": {"bg": "#e3f2fd", "border": "#2196f3", "text": "#1565c0"},
        "warning": {"bg": "#fff3e0", "border": "#ff9800", "text": "#e65100"},
        "error": {"bg": "#ffebee", "border": "#f44336", "text": "#c62828"}
    }
    
    colors = color_map.get(status_type, color_map["info"])
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h2 style="color: {colors['text']}; margin: 0 0 20px 0;">{title}</h2>
        <div style="background-color: {colors['bg']}; padding: 15px; border-radius: 6px; border-left: 3px solid {colors['border']};">
            <p style="margin: 0; color: {colors['text']}; line-height: 1.5;">
                {message}
            </p>
        </div>
        <p style="margin: 15px 0 0 0; color: #666; font-size: 12px;">
            Timestamp: {get_nepal_time().strftime('%Y-%m-%d %H:%M:%S')} NPT
        </p>
    </div>
</body>
</html>
"""