"""
tool_outreach_automated_sender.py
=================================
Generates a hyper-personalized outreach email using Groq/Llama 3
and sends it via Gmail SMTP or SendGrid.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq


async def tool_outreach_automated_sender(
    company: str,
    signals: list[str],
    account_brief: str,
    recipient_email: str,
    recipient_name: str,
    icp: str,
) -> dict:
    """
    Generate and send a personalized outreach email.

    Args:
        company:         Target company name
        signals:         List of signal strings
        account_brief:   Account brief from research_analyst
        recipient_email: Email address to send to
        icp:             Ideal Customer Profile

    Returns:
        Dict with email_sent status, subject, and body.
    """
    # ── 1. Generate email content via LLM ───────────────────────────────────
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    signals_text = "\n".join(f"- {s}" for s in signals)

    prompt = f"""You are a world-class B2B sales copywriter. Write a personalized cold outreach email.

TARGET COMPANY: {company}
RECIPIENT EMAIL: {recipient_email}
RECIPIENT NAME: {recipient_name if recipient_name else 'Unknown (use company team name instead, e.g. Hi ' + company + ' Team)'}

SIGNALS WE CAPTURED:
{signals_text}

ACCOUNT BRIEF:
{account_brief}

OUR ICP / WHAT WE SELL:
{icp}

INSTRUCTIONS:
1. Write a compelling subject line (include an emoji). Reference the company name.
2. Address the recipient as "{recipient_name if recipient_name else company + ' Team'}" in the greeting.
3. Start with a personalized opening that mentions a SPECIFIC signal.
4. Connect their situation to our offering naturally.
5. End with a soft CTA (not pushy).
6. Keep it under 150 words.
7. Tone: warm, human, conversational — NOT salesy.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
SUBJECT: [your subject line]
BODY:
[your email body]

Do NOT add any other text or explanations."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a world-class B2B outreach copywriter."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=400,
    )

    raw_output = response.choices[0].message.content.strip()

    # ── 2. Parse subject and body ───────────────────────────────────────────
    subject = ""
    body = ""

    if "SUBJECT:" in raw_output and "BODY:" in raw_output:
        parts = raw_output.split("BODY:", 1)
        subject = parts[0].replace("SUBJECT:", "").strip()
        body = parts[1].strip()
    else:
        # Fallback parsing
        lines = raw_output.split("\n", 1)
        subject = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else raw_output

    # ── 3. Send the email ───────────────────────────────────────────────────
    email_sent = False
    send_method = "none"
    error_message = ""

    # Method 1: Gmail SMTP (Recommended)
    smtp_email = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "")

    if smtp_email and smtp_password:
        print(f"[OutreachSender] Attempting Gmail SMTP with {smtp_email}...")
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.set_debuglevel(0)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, recipient_email, msg.as_string())

            email_sent = True
            send_method = "gmail_smtp"
            print(f"[OutreachSender] ✅ Email sent via Gmail SMTP to {recipient_email}")
        except smtplib.SMTPAuthenticationError as e:
            error_message = f"Gmail authentication failed. Check SMTP_EMAIL and SMTP_APP_PASSWORD. Error: {e}"
            print(f"[OutreachSender] ❌ {error_message}")
        except smtplib.SMTPException as e:
            error_message = f"Gmail SMTP error: {e}"
            print(f"[OutreachSender] ❌ {error_message}")
        except Exception as e:
            error_message = f"Gmail connection error: {type(e).__name__}: {e}"
            print(f"[OutreachSender] ❌ {error_message}")
    else:
        print(f"[OutreachSender] ⚠️ Gmail SMTP not configured (SMTP_EMAIL={bool(smtp_email)}, SMTP_APP_PASSWORD={bool(smtp_password)})")

    # Method 2: SendGrid (Fallback)
    if not email_sent:
        sendgrid_key = os.getenv("SENDGRID_API_KEY", "")
        sendgrid_from = os.getenv("SENDGRID_FROM_EMAIL", "")

        if sendgrid_key and sendgrid_from:
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail

                sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
                message = Mail(
                    from_email=sendgrid_from,
                    to_emails=recipient_email,
                    subject=subject,
                    plain_text_content=body,
                )
                sg.send(message)
                email_sent = True
                send_method = "sendgrid"
                print(f"[OutreachSender] ✅ Email sent via SendGrid to {recipient_email}")
            except Exception as e:
                error_message = f"SendGrid error: {e}"
                print(f"[OutreachSender] ❌ {error_message}")

    # Method 3: Log to console (Dev fallback — does NOT actually send)
    if not email_sent:
        send_method = "preview_only"
        print("\n" + "=" * 60)
        print("📧  EMAIL PREVIEW (Email NOT sent — no working email service)")
        print("=" * 60)
        print(f"To:      {recipient_email}")
        print(f"Subject: {subject}")
        print(f"\n{body}")
        print("=" * 60)
        if error_message:
            print(f"Error: {error_message}")
        print()

    return {
        "email_sent": email_sent,
        "send_method": send_method,
        "error_message": error_message,
        "subject": subject,
        "body": body,
    }
