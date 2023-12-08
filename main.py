import imaplib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    # Gmail IMAP server address and port
    GMAIL_IMAP_SERVER = "imap.gmail.com"
    GMAIL_IMAP_PORT = 993

    # Load the stored environment variables
    load_dotenv()

    # User credentials
    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    # Address list you want to delete emails from
    addresses = []

    # Connect to the Gmail IMAP server
    with imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER, GMAIL_IMAP_PORT) as mail:
        # Login to your account
        mail.login(username, password)

        del_unopened_emails(mail)
        del_spam_emails(mail)
        del_emails_from_list(mail, addresses)

        # Logout
        mail.logout()

def del_unopened_emails(mail):
    date_days_ago = get_date_days_ago(15)
    del_emails(mail, date_days_ago, None, "inbox", "UNSEEN")

def del_spam_emails(mail):
    date_days_ago = get_date_days_ago(0)
    del_emails(mail, date_days_ago, None, '"[Gmail]/Spam"', "ALL")

def del_emails_from_list(mail, addresses):
    date_days_ago = get_date_days_ago(15)
    del_emails(mail, date_days_ago, addresses, "inbox", "ALL")

def get_date_days_ago(days):
    return (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")    

def del_emails(mail, date_days_ago, addresses, location, search_type):
    mail.select(location)
    print(f"Deleting emails from {location} before {date_days_ago}...")

    if addresses:
        for address in addresses:
            status, messages = mail.search(None, f'({search_type} FROM {address} BEFORE {date_days_ago})')
            handle_del(mail, messages)
    else:
        status, messages = mail.search(None, f'({search_type} BEFORE {date_days_ago})')
        handle_del(mail, messages)

def handle_del(mail, messages):
    BATCH_SIZE = 100  # Define the batch size

    # Decode byte string to a regular string and then split
    message_str = messages[0].decode('utf-8')
    message_ids = message_str.split()

    
    for i in range(0, len(message_ids), BATCH_SIZE):
        batch = message_ids[i:i + BATCH_SIZE]
        
        for message in batch:
            mail.store(message, "+FLAGS", "\\Deleted")

        print("Expunging...")
        mail.expunge() 

main()