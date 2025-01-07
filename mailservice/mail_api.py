import requests
import logging
from jinja2 import Environment, FileSystemLoader
import yaml
import os


logger = logging.getLogger("EmailService")

def load_config(config_file):
 
    if not os.path.exists(config_file):
        logger.error(f"Configuration file not found: {config_file}")
        exit(1)
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Loaded configuration from {config_file}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Error reading configuration file: {e}")
        exit(1)

def render_email_template(template_name, context):
 
    try:
        env = Environment(loader=FileSystemLoader('templates'))  # Templates folder
        template = env.get_template(template_name)
        return template.render(context)
    except Exception as e:
        logger.error(f"Failed to render email template. Error: {e}")
        return None

def send_email(api_url, email_data):
 
    try:
        headers = {
            "Content-Type": "application/json"
        }
        logger.info(f"Sending email to API: {api_url}")
        logger.debug(f"Email data: {email_data}")

        response = requests.post(api_url, json=email_data, headers=headers)
        response.raise_for_status()

        logger.info(f"Email sent successfully. Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email. Error: {e}")
        return None

# Load configuration
config = load_config('config.yaml')

# Read values from the configuration file
email_service_config = config['EmailService']
recipients_config = config['Recipients']
attachments_config = config['Attachments']
binary_attachments_config = config['BinaryAttachments']

api_url = email_service_config['api_url']
email_from = email_service_config['from']
subject = email_service_config['subject']
remarks = email_service_config['remarks']
contactus = email_service_config['contactus']
recipients = recipients_config['to']
cc = recipients_config['cc']
bcc = recipients_config['bcc']
attachments = attachments_config
binary_attachments = binary_attachments_config

# Render the email body
template_context = {
    "recipient_name": "John Doe",
    "body_content": "This is a test email sent using a template.",
    "sender_name": "Your Company"
}
email_body = render_email_template('email_template.html', template_context)
if not email_body:
    logger.error("Email body rendering failed. Exiting.")
    exit(1)

# Prepare email data
email_data = {
    "from": email_from,
    "recipients": recipients,
    "subject": subject,
    "body": email_body,
    "remarks": remarks,
    "contactus": contactus,
    "cc": cc,
    "bcc": bcc,
    "attachments": attachments,
    "binaryAttachments": binary_attachments
}

# Send the email
response = send_email(api_url, email_data)
if response:
    logger.info("Email process completed successfully.")
else:
    logger.warning("Email process encountered an issue.")
