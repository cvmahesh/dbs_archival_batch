import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email details
sender_email = "cvmahesh@rediffmail.com"  # Replace with your email
receiver_email = "rush2cvmahesh@gmail.com"  # Replace with the recipient's email
password = "GautamM"  # Replace with your email password

# Email content
subject = "Test Email from Python"
body = "This is a test email sent using Python's smtplib library."

# Create the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    # Connect to the server
    with smtplib.SMTP("smtp.rediffmail.com", 587) as server:
        server.starttls()  # Start TLS for security
        server.login(sender_email, password)  # Login to the email account
        server.send_message(message)  # Send the email
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
