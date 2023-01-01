import base64
from email.message import EmailMessage

import httplib2
import oauth2client
from apiclient import discovery
from oauth2client import client, tools, file

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Backup Service'
MAIL = "seyahdoo@gmail.com"


def get_credentials():
    credential_path = 'gmail_credentials.json'
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def send_message(sender, to, subject, content):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message = create_message(sender, to, subject, content)
    result = (service.users().messages().send(userId="me", body=message).execute())
    return result


def create_message(sender, to, subject, content):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.set_content(content)
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def send_mail_to_myself(subject, content):
    send_message(MAIL, MAIL, subject, content)
    return

