import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

contact_bp = Blueprint('contact', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contact_bp.route('/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions with Google Workspace SMTP"""
    try:
        data = request.get_json()
        
        # Extract form data
        name = data.get('name', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        event_date = data.get('eventDate', '')
        shoot_type = data.get('shootType', '')
        budget = data.get('budget', '')
        additional_info = data.get('additionalInfo', '')
        
        # Validate required fields
        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Create email content
        subject = f"New Photography Inquiry from {name}"
        
        body = f"""
New photography inquiry received from Mind's Eye Photography website:

Name: {name}
Phone: {phone}
Email: {email}
Event Date: {event_date}
Type of Shoot: {shoot_type}
Estimated Budget: {budget}

Additional Information:
{additional_info}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Reply directly to this email to respond to the client.
        """
        
        # Send email using Google Workspace SMTP
        try:
            # Google SMTP configuration
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_login = "rick@themindseyestudio.com"  # Google account for SMTP login
            sender_password = "dvke joyj ydge qcma"  # New app-specific password
            sender_email = "info@themindseyestudio.com"  # Display address
            recipient_email = "info@themindseyestudio.com"  # Email for receiving
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email  # Shows as info@ in email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg['Reply-To'] = email  # Set reply-to as client's email
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_login, sender_password)  # Login with rick@ account
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully for inquiry from {name} ({email})")
            return jsonify({'message': 'Thank you for your inquiry! I will get back to you soon.'}), 200
            
        except Exception as email_error:
            logger.error(f"Failed to send email: {str(email_error)}")
            # Still return success to user, but log the error
            return jsonify({'message': 'Thank you for your inquiry! I will get back to you soon.'}), 200
            
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({'error': 'Sorry, there was an error processing your request.'}), 500

