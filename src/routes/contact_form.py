"""
Contact Form with Google SMTP Integration
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from datetime import datetime

contact_bp = Blueprint('contact_form', __name__)

# Google SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'rick@themindseyestudio.com'  # Login username
SMTP_PASSWORD = 'dvke joyj ydge qcma'  # Updated Google app password

@contact_bp.route('/api/contact', methods=['POST'])
def send_contact_form():
    """Handle contact form submission with Google SMTP"""
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        photography_type = data.get('photography_type', '').strip()
        message = data.get('message', '').strip()
        
        # Validate required fields
        if not all([name, email, message]):
            return jsonify({
                'success': False,
                'error': 'Name, email, and message are required fields.'
            }), 400
        
        # Create email content
        subject = f"New Contact Form Submission - {photography_type if photography_type else 'General Inquiry'}"
        
        # HTML email template
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ff6b35; border-bottom: 2px solid #ff6b35; padding-bottom: 10px;">
                    New Contact Form Submission
                </h2>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1e293b; margin-top: 0;">Contact Information</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    {f'<p><strong>Phone:</strong> {phone}</p>' if phone else ''}
                    {f'<p><strong>Photography Type:</strong> {photography_type}</p>' if photography_type else ''}
                </div>
                
                <div style="background: #fff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #1e293b; margin-top: 0;">Message</h3>
                    <p style="white-space: pre-wrap;">{message}</p>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e0f2fe; border-radius: 8px; font-size: 14px; color: #0277bd;">
                    <p><strong>Submitted:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>From:</strong> Mind's Eye Photography Website Contact Form</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
New Contact Form Submission - Mind's Eye Photography

Contact Information:
Name: {name}
Email: {email}
{f'Phone: {phone}' if phone else ''}
{f'Photography Type: {photography_type}' if photography_type else ''}

Message:
{message}

Submitted: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
From: Mind's Eye Photography Website Contact Form
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME  # Send to yourself
        msg['Reply-To'] = email  # Set reply-to as the sender's email
        
        # Attach both plain text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email via Google SMTP
        if not SMTP_PASSWORD:
            return jsonify({
                'success': False,
                'error': 'Email service not configured. Please contact us directly at info@themindseyestudio.com'
            }), 500
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message! We will get back to you soon.'
        })
        
    except smtplib.SMTPAuthenticationError:
        return jsonify({
            'success': False,
            'error': 'Email authentication failed. Please contact us directly at info@themindseyestudio.com'
        }), 500
        
    except smtplib.SMTPException as e:
        return jsonify({
            'success': False,
            'error': 'Email service temporarily unavailable. Please contact us directly at info@themindseyestudio.com'
        }), 500
        
    except Exception as e:
        print(f"Contact form error: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while sending your message. Please contact us directly at info@themindseyestudio.com'
        }), 500

