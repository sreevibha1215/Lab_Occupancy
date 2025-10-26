import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        # For production, use environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "lab.reservation@vnrvjiet.edu"  # Replace with actual email
        self.sender_password = "your_app_password"  # Replace with actual app password
        
        # For development/testing, we'll just log emails
        self.testing_mode = True
        
    def send_email(self, recipient, subject, body_html):
        """Send email (or log it in testing mode)"""
        if self.testing_mode:
            logger.info(f"\n{'='*60}\nEMAIL NOTIFICATION\n{'='*60}")
            logger.info(f"To: {recipient}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body_html}")
            logger.info(f"{'='*60}\n")
            return True
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.sender_email
            message["To"] = recipient
            message["Subject"] = subject
            
            html_part = MIMEText(body_html, "html")
            message.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False
    
    def send_approval_email(self, user_email, lab_number, date, start_time, end_time, reservation_id):
        """Send reservation approval confirmation"""
        subject = f"✅ Lab Reservation Approved - {lab_number}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #10b981; text-align: center;">🎉 Reservation Approved!</h2>
                
                <p style="font-size: 16px;">Dear User,</p>
                
                <p style="font-size: 16px;">
                    Your lab reservation has been <strong>approved</strong>. Here are the details:
                </p>
                
                <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Lab:</strong> {lab_number}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {start_time} - {end_time}</p>
                    <p style="margin: 5px 0;"><strong>Reservation ID:</strong> #{reservation_id}</p>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Please arrive on time and ensure the lab is left clean after use.
                </p>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    If you need to modify or cancel this reservation, please do so at least 24 hours in advance.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    VNRVJIET Lab Reservation System<br>
                    This is an automated message. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_pending_email(self, user_email, lab_number, date, start_time, end_time, alternatives):
        """Send notification for pending reservation with alternatives"""
        subject = f"⏳ Lab Reservation Pending - {lab_number}"
        
        # Build alternatives HTML
        alt_labs_html = ""
        if alternatives.get('alternative_labs'):
            alt_labs_html = "<h4 style='color: #3b82f6;'>Alternative Labs Available:</h4><ul>"
            for alt in alternatives['alternative_labs'][:3]:
                alt_labs_html += f"<li><strong>{alt['lab_number']}</strong> (Floor {alt['floor']}, Capacity: {alt['capacity']})</li>"
            alt_labs_html += "</ul>"
        
        alt_times_html = ""
        if alternatives.get('alternative_times'):
            alt_times_html = "<h4 style='color: #3b82f6;'>Alternative Time Slots:</h4><ul>"
            for alt in alternatives['alternative_times']:
                alt_times_html += f"<li>{alt['start_time']} - {alt['end_time']} ({alt['session']})</li>"
            alt_times_html += "</ul>"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #f59e0b; text-align: center;">⏳ Reservation Pending Review</h2>
                
                <p style="font-size: 16px;">Dear User,</p>
                
                <p style="font-size: 16px;">
                    Your lab reservation request is currently <strong>pending</strong> administrative approval.
                </p>
                
                <div style="background-color: #fffbeb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Requested Lab:</strong> {lab_number}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {start_time} - {end_time}</p>
                </div>
                
                {alt_labs_html}
                {alt_times_html}
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    You will receive a confirmation email once your reservation is processed.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    VNRVJIET Lab Reservation System<br>
                    This is an automated message. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_rejection_email(self, user_email, lab_number, date, start_time, end_time, reason):
        """Send rejection notification"""
        subject = f"❌ Lab Reservation Update - {lab_number}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #ef4444; text-align: center;">⚠️ Reservation Status Update</h2>
                
                <p style="font-size: 16px;">Dear User,</p>
                
                <p style="font-size: 16px;">
                    We regret to inform you that your lab reservation has been updated due to: <strong>{reason}</strong>
                </p>
                
                <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Lab:</strong> {lab_number}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {start_time} - {end_time}</p>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Please submit a new reservation request or contact the administration for assistance.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    VNRVJIET Lab Reservation System<br>
                    This is an automated message. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_modification_email(self, user_email, lab_number, updates):
        """Send notification for reservation modification"""
        subject = f"✏️ Lab Reservation Modified - {lab_number}"
        
        updates_html = "<ul>"
        for key, value in updates.items():
            updates_html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        updates_html += "</ul>"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #3b82f6; text-align: center;">✏️ Reservation Modified</h2>
                
                <p style="font-size: 16px;">Dear User,</p>
                
                <p style="font-size: 16px;">
                    Your lab reservation for <strong>{lab_number}</strong> has been modified. The following changes have been made:
                </p>
                
                <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    {updates_html}
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Your reservation is now pending re-approval. You will receive a confirmation email once processed.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    VNRVJIET Lab Reservation System<br>
                    This is an automated message. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_cancellation_email(self, user_email, lab_number, date, start_time, end_time):
        """Send cancellation confirmation"""
        subject = f"🚫 Lab Reservation Cancelled - {lab_number}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #64748b; text-align: center;">🚫 Reservation Cancelled</h2>
                
                <p style="font-size: 16px;">Dear User,</p>
                
                <p style="font-size: 16px;">
                    Your lab reservation has been successfully <strong>cancelled</strong>.
                </p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Lab:</strong> {lab_number}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {start_time} - {end_time}</p>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    You can submit a new reservation request at any time through the portal.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    VNRVJIET Lab Reservation System<br>
                    This is an automated message. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)

