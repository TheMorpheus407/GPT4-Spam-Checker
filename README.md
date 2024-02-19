### Important Note: This is a proof of concept on how AI may benefit Spam detection in E-Mails. It is NOT designed to be actually used, since it has major downsides. Rather I wanted to study and evaluate how it could be used.
### You can find my concerns and the development of this script here: https://youtu.be/XFQUgWphwF8

# Email Processing System

This Email Processing System is designed to download, analyze, and forward emails automatically. It uses OpenAI's GPT-4 for spam detection, intelligently filtering emails before forwarding them to specified addresses. Additionally, it features a logging mechanism to track its operations and decisions.

## Features

- **Email Downloading**: Connects to an IMAP server to fetch unread emails, marking them as read post-download.
- **Spam Detection**: Utilizes OpenAI's GPT-4 model to analyze emails for spam content.
- **Email Forwarding**: Forwards non-spam emails to predefined email addresses, preserving their original format.
- **Logging**: Records operations, including spam detection scores and forwarding actions, with UTF-8 encoding support for international characters.

## Dependencies

This project relies on the following Python modules:

- `imaplib`
- `re`
- `smtplib`
- `email`
- `openai`
- `configparser`
- `logging`

Make sure to install the OpenAI Python module using pip:

```bash
pip install openai
```

## Configuration

Before running the system, configure the following in `configuration.ini`:

- IMAP server details
- Email account credentials
- OpenAI API key

Example `configuration.ini`:

```ini
[DEFAULT]
imap_server = imap.example.com
email_account = your_email@example.com
email_password = your_password
openai_api_key = your_openai_api_key
```

## Usage

To start the email processing system, run the `main` function within the script. Ensure that your `configuration.ini` is set up correctly with your email and OpenAI API details.

The system performs the following operations in order:

1. Downloads unread emails from the specified IMAP server.
2. Analyzes each email for spam content using OpenAI's GPT-4.
3. Forwards emails deemed not to be spam to the configured recipient addresses.
4. Logs all operations, including spam scores and forwarding actions.

## Logging

Logs are stored in `app.log`. The logging system is set up to handle UTF-8 encoded characters, ensuring that international characters are logged correctly.

## Contributing

Since this is one of many projects, this is rather to illustrate a point and not to actively continued - I simply don't have the capacities to maintain it. But feel free to fork and use it at your own peril.
