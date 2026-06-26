import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import markdown
import config

def generate_html_body(videos, ai_summary):
    """
    Generates a beautifully designed, responsive HTML email body.
    """
    # Convert Gemini's markdown summary to HTML
    ai_html = ""
    if ai_summary:
        ai_html = markdown.markdown(ai_summary)
    else:
        ai_html = "<p>No AI analysis available for today.</p>"

    # Build video list HTML
    videos_html = ""
    if not videos:
        videos_html = "<p style='color: #a1a1aa;'>No videos exceeded the outperformance threshold in the last 48 hours.</p>"
    else:
        for v in videos:
            videos_html += f"""
            <div style="background-color: #1e1e24; border-radius: 8px; padding: 16px; margin-bottom: 16px; border-left: 4px solid #8b5cf6;">
                <h3 style="margin-top: 0; margin-bottom: 8px;">
                    <a href="https://www.youtube.com/watch?v={v['video_id']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 16px; font-weight: bold;">
                        {v['title']}
                    </a>
                </h3>
                <p style="color: #e4e4e7; margin: 4px 0; font-size: 14px;"><strong>Channel:</strong> {v['channel_title']}</p>
                <div style="margin: 8px 0; font-size: 13px;">
                    <span style="background-color: #27272a; color: #10b981; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 8px;">
                        🔥 {v['outperformance_ratio']:.2f}x average
                    </span>
                    <span style="background-color: #27272a; color: #3b82f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 8px;">
                        👀 {v['views']:,} views
                    </span>
                    <span style="color: #a1a1aa;">
                        📅 {v['published_at']}
                    </span>
                </div>
                <p style="color: #a1a1aa; font-size: 13px; margin-bottom: 0; line-height: 1.4;">
                    {v['description'][:200]}...
                </p>
            </div>
            """

    # Complete HTML email template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily AI YouTube Outperformance Report</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #0c0c0e;
                color: #f4f4f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 24px;
            }}
            .header {{
                text-align: center;
                padding-bottom: 24px;
                border-bottom: 1px solid #27272a;
            }}
            .header h1 {{
                font-size: 24px;
                margin: 0;
                background: linear-gradient(to right, #8b5cf6, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .section {{
                margin-top: 24px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 6px;
                margin-bottom: 16px;
                color: #3b82f6;
            }}
            /* Gemini Markdown Styling */
            .ai-report h1, .ai-report h2, .ai-report h3 {{
                color: #8b5cf6;
                margin-top: 16px;
                margin-bottom: 8px;
            }}
            .ai-report p {{
                line-height: 1.6;
                color: #e4e4e7;
                font-size: 14px;
            }}
            .ai-report ul, .ai-report ol {{
                color: #e4e4e7;
                font-size: 14px;
                line-height: 1.6;
                padding-left: 20px;
            }}
            .ai-report li {{
                margin-bottom: 8px;
            }}
            .footer {{
                text-align: center;
                padding-top: 24px;
                border-top: 1px solid #27272a;
                margin-top: 32px;
                font-size: 12px;
                color: #71717a;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎙️ AI YouTube Channel Strategy Hub</h1>
                <p style="color: #a1a1aa; margin: 4px 0 0 0; font-size: 14px;">Daily Outperformance & Trend Analysis Report</p>
            </div>
            
            <div class="section">
                <div class="section-title">🔥 Outperforming Videos in last 48 hours</div>
                {videos_html}
            </div>
            
            <div class="section">
                <div class="section-title">🤖 AI Trend Curations & Channel Insights</div>
                <div class="ai-report" style="background-color: #18181b; border-radius: 8px; padding: 16px; border: 1px solid #27272a;">
                    {ai_html}
                </div>
            </div>
            
            <div class="footer">
                <p>Sent automatically from your Hostinger KVM1 VPS.</p>
                <p>To configure your tracking settings, edit config.py or your .env file.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def send_email_via_resend(html_content, subject):
    """
    Sends email using Resend API.
    """
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {config.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Resend default sandbox sender requires sending to verified email (which is the account owner's email)
    # If the user sets up a custom domain, they can customize this.
    sender = "AI Tracker <onboarding@resend.dev>"
    if "resend.dev" not in config.SENDER_EMAIL:
        sender = config.SENDER_EMAIL

    payload = {
        "from": sender,
        "to": [config.RECIPIENT_EMAIL],
        "subject": subject,
        "html": html_content
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print("Email sent successfully via Resend API!")
            return True
        else:
            print(f"Failed to send email via Resend API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending email via Resend: {e}")
        return False

def send_email_via_smtp(html_content, subject):
    """
    SMTP Fallback (if SMTP credentials are provided in env).
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_server, smtp_user, smtp_pass]):
        print("SMTP settings are not configured. Skipping SMTP email sending.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = config.RECIPIENT_EMAIL

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # Connect to server
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(config.SENDER_EMAIL, config.RECIPIENT_EMAIL, msg.as_string())
        server.close()
        print("Email sent successfully via SMTP!")
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False

def send_report(videos, ai_summary):
    """
    Helper function to decide which email method to use.
    """
    subject = "📈 Daily AI YouTube Outperformance Report"
    html_content = generate_html_body(videos, ai_summary)
    
    if config.RESEND_API_KEY:
        print("Attempting to send email via Resend API...")
        return send_email_via_resend(html_content, subject)
    else:
        print("No Resend API Key found. Attempting SMTP fallback...")
        import os
        return send_email_via_smtp(html_content, subject)
