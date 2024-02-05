import imaplib
import re
import smtplib
import email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
import configparser
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Sets up the logging configuration.
    Logs will be stored in 'app.log' and rotate after reaching a certain size.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=10000000000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def load_configuration(config_file='configuration.ini'):
    """
    Loads configuration settings from a .ini file.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def check_for_spam(email_content):
    """
    Uses OpenAI's GPT-4 to determine if the provided email content is spam.
    Returns True if spam, False otherwise.
    """
    try:
        messages = [
            {"role": "system",
             "content": "You are a highly intelligent email filter. You check if an email is fraudulent"},
            {"role": "system",
             "content": "You check the emails sender and for forwarded emails you will check the original sender."},
            {"role": "system",
             "content": "If you receive a business mail that is supposedly from paypal, the sender has to be paypal and not paypal@email.cz for example."},
            {"role": "system",
             "content": "You check if there are links in the email and if there are, if they are legit."},
            {"role": "system",
             "content": "When checking if a link is legit, you look at the domain and tell if it is what it suggests to the user to be."},
            {"role": "system",
             "content": "For example google--drive.somesite.com suggests, it is google drive, when it is actually somesite.com"},
            {"role": "system",
             "content": "If there are attachments in the file, you will check if this really makes sense. A PDF with invoice is common, however executable files, docx or js is highly dangerous."},
            {"role": "system",
             "content": "Also, you will inspect the content of the mail. If the language is urgent or threatening, this might be an indicator."},
            {"role": "system",
             "content": "If the sender looks suspicious and asks for personal information, this is also a strong indicator."},
            {"role": "system",
             "content": "If there are elements in the mail, that don't fit, what it's trying to say, for example a dead link in the footer, this is another indicator."},
            {"role": "system", "content": "Generic Greetings are also a sign of broadly targeted phishing."},
            {"role": "system", "content": "Use the entire email and go for your feeling with it."},
            {"role": "system", "content": "Ignore ratings of others like X-Spam-Level or X-Spam-Status."},
            {"role": "system",
             "content": "Your output will be a number ranging from 0 to 100 indicating the percentage feeling of the mail being fraudulent."},
            {"role": "system", "content": "100 means: This email is absolutely phishy and scam or fraudulent."},
            {"role": "system", "content": "0 means: This email is totally trustworthy."},
            {"role": "system", "content": "You will not output anything but this number."},
            {"role": "user", "content": email_content}
        ]
        model = "gpt-4-1106-preview"

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

        # Analyze response to determine if it's spam
        answer = response.choices[0].message.content
        match = re.search(r'\b(\d{1,3})\b', answer)
        if match:
            spam_score = int(match.group(1))
            logger.info(f"Spam score: {spam_score} for {email_content}")

            # Decide if it's spam based on the score
            is_spam = spam_score > 50  # Example threshold, can be adjusted
            return is_spam
        else:
            logger.warning("No spam score found in the model's response.")
            return False
    except Exception as e:
        logger.error(f"Error in check_for_spam: {e}")
        return False


def download_emails(imap_server, email_account, email_password):
    """
    Connects to the IMAP server and downloads unread emails, marking them as read.
    Returns a list of tuples, each containing an email.message.EmailMessage object and its decoded body.
    """
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_account, email_password)
        mail.select('inbox')

        status, email_ids = mail.search(None, 'UNSEEN')
        if status != 'OK':
            logger.error("No new emails to download.")
            return []

        emails = []
        for e_id in email_ids[0].split():
            status, data = mail.fetch(e_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"Failed to fetch email {e_id}.")
                continue

            # Parse email content
            msg = email.message_from_bytes(data[0][1])
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" not in content_disposition and content_type == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8')
                        except UnicodeDecodeError:
                            body = part.get_payload(decode=True).decode('latin-1')  # Fallback encoding
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    body = msg.get_payload(decode=True).decode('latin-1')  # Fallback encoding

            emails.append((msg, body))

            # Mark email as read
            mail.store(e_id, '+FLAGS', '\\Seen')

        mail.close()
        mail.logout()
        return emails
    except Exception as e:
        logger.error(f"An error occurred in download_emails: {e}")
        return []


def forward_email(smtp_server, email_account, email_password, original_email):
    """
    Forwards an email to a specified recipient using SMTP, keeping the original structure and signature.
    """
    #TODO
    return
    try:
        # Recipient address
        #TODO
        recipient = "ALIAS@use.startmail.com"

        # Decode and set the subject of the original email
        subject = decode_header(original_email['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Create a MIME message for forwarding
        forwarded_msg = MIMEMultipart()
        forwarded_msg['From'] = email_account
        forwarded_msg['To'] = recipient
        forwarded_msg['Subject'] = f"Fwd: {subject}"

        # Attach the original email content
        for part in original_email.walk():
            forwarded_msg.attach(part)

        # SMTP session to send the email
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(email_account, email_password)
        server.send_message(forwarded_msg)
        server.quit()

        logger.info(f"Email forwarded to {recipient}")
    except Exception as e:
        logger.error(f"An error occurred in forward_email: {e}")


config = load_configuration()
client = OpenAI(api_key=config['DEFAULT']['openai_api_key'])
logger = setup_logging()


def main():
    """
    Main function to orchestrate the downloading, spam checking, and forwarding of emails.
    """
    try:
        logger.info("Starting email processing")

        # Download emails
        emails = download_emails(config['DEFAULT']['imap_server'],
                                 config['DEFAULT']['email_account'],
                                 config['DEFAULT']['email_password'])

        for email_msg, email_body in emails:
            # Check for spam
            if not check_for_spam(str(email_msg) + email_body):
                # Forward non-spam emails
                forward_email(config['DEFAULT']['smtp_server'],
                              config['DEFAULT']['email_account'],
                              config['DEFAULT']['email_password'],
                              email_msg)

        logger.info("Email processing completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
