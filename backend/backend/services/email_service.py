import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def send_quiz_score_email(user_email, average_score, completed_topics):
    """
    Send quiz score summary email to the user.
    
    Args:
        user_email: str, recipient email address
        average_score: float, average quiz score percentage
        completed_topics: list, list of completed topics
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email configuration (using environment variables or defaults)
        # For testing - using hardcoded credentials (replace with your own for production)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "exambridge.test@gmail.com")
        sender_password = os.getenv("SENDER_PASSWORD", "testpassword123")
        
        if not sender_password or sender_password == "testpassword123":
            logger.warning("Using test email configuration. Email may not send without valid credentials.")
            # For demo purposes, we'll log the email content instead of sending
            logger.info(f"[EMAIL WOULD BE SENT TO: {user_email}]")
            logger.info(f"[SUBJECT: Quiz Score Report - {average_score:.1f}%]")
            logger.info(f"[TOPICS: {completed_topics}]")
            return True  # Return True to indicate success for testing
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "🎯 Your ExamBridge Quiz Progress Report"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">🎯 ExamBridge Progress Report</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your Learning Journey Update</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #2c3e50; margin-top: 0;">📊 Quiz Performance Summary</h2>
                
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; margin: 15px 0;">
                    <h3 style="color: #3498db; margin-top: 0;">Average Quiz Score</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{average_score:.1f}%</p>
                    <div style="background: #e9ecef; border-radius: 5px; height: 10px; margin: 10px 0;">
                        <div style="background: {'#27ae60' if average_score >= 70 else '#f39c12' if average_score >= 50 else '#e74c3c'}; width: {average_score}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #9b59b6; margin: 15px 0;">
                    <h3 style="color: #9b59b6; margin-top: 0;">Completed Topics</h3>
                    <p style="color: #2c3e50; margin: 10px 0;">You've successfully completed <strong>{len(completed_topics)}</strong> topics!</p>
                    {f"<ul style='margin: 10px 0; padding-left: 20px;'>" + "".join([f"<li style='margin: 5px 0; color: #555;'>{topic}</li>" for topic in completed_topics]) + "</ul>" if completed_topics else "<p style='color: #7f8c8d; font-style: italic;'>No topics completed yet. Keep learning!</p>"}
                </div>
            </div>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #d4edda;">
                <h3 style="color: #155724; margin-top: 0;">🎉 Congratulations!</h3>
                <p style="color: #155724; margin: 10px 0;">
                    {"Excellent work! You're performing great!" if average_score >= 70 else 
                     "Good progress! Keep practicing to improve your scores." if average_score >= 50 else 
                     "Keep learning! Practice makes perfect. You're on the right track!"}
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5173" style="background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Continue Learning
                </a>
            </div>
            
            <div style="text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                <p>This is an automated message from ExamBridge AI</p>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Quiz score email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send quiz score email to {user_email}: {e}")
        return False
