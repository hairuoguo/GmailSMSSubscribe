from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

from __future__ import print_function
import httplib2
import os

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SMS Subscribe'

def main():

def format_session_info():

    #get all emails from labels
    #parse
    #only 1 email - sign up for all sessions
    #different emails (one for each session) - apply to specific session
    #output csv
    #TODO: how to handle error codes

def ask_for_email(): #ask emails from all numbers that didn't have any

def create_mailing_lists(session_info): #make mailing lists for each label
    
def send_emails_to_all(email_list, message):

 

if name == "__main__":
    main()
