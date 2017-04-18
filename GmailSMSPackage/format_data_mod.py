from __future__ import print_function
import httplib2
import os
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors
import base64
import email
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

import credentials_mod as cm
import label_threads_mod as lt

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


def address_is_phone(address):
    match = get_phone_from_text(address)
    if match is not None:
        return True
    else:
        return False

'''
def address_is_email(address):
    email_string = re.compile('([a-zA-Z0-9_\-.]+\@[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)')
    match = email_string.match(address)
    if match is not None:
        return True
    else:
        return False
'''
    
def get_email_from_text(text):
    email_string = re.compile('([a-zA-Z0-9_\-.]+\@[a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*)')
    match = re.findall(email_string, text)
    return match

def get_phone_from_text(text):
    phone_string = re.compile('(\([0-9]{3}\) [0-9]{3}-[0-9]{4})') 
    match = phone_string.search(text)
    return match

def format_session_info(label_names): #add start_day functionality later
    service = cm.create_service()
    session_addresses = {label_name: {'from_emails': set()} for label_name in label_names}
    provider_addresses = {}
    label_ids, label_ids_to_names = lt.get_label_ids(label_names)
    user_id = 'me'
    message_format = "full"
    try:
        for label_id in label_ids:
            label_name = label_ids_to_names[label_id]
            message_ids = cm.get_message_ids(service, label_id)
            for message in message_ids:
                try:
                    message_data = service.users().messages().get(userId=user_id, id=message, format=message_format).execute()
                    #print(message_data['payload']['parts'])
                    from_data = filter(lambda x: x['name'] == 'From', message_data['payload']['headers'])
                    if len(from_data) == 0:
                        continue
                    from_value = from_data[0]['value'].encode('UTF-8')
                    
                    body_data = message_data['payload']['parts'][0]['body']['data'].encode('UTF-8')
                    body_value = base64.urlsafe_b64decode(body_data)
                    if address_is_phone(from_value):
                        phone_number = get_phone_from_text(from_value).group()
                        email_matches = get_email_from_text(body_value)
                        if phone_number not in provider_addresses:
                            provider_addresses[phone_number] = get_email_from_text(from_value)[0]
                        if phone_number in session_addresses[label_name].keys():
                            session_addresses[label_name][phone_number].update(email_matches)
                        else:
                            session_addresses[label_name][phone_number] = set(email_matches)
                    else:
                        email_address = get_email_from_text(from_value)
                        session_addresses[label_name]['from_emails'].update(email_address)
                except errors.HttpError, error:
                    print(error)
                    continue
    except errors.HttpError, error:
        print(error)
        pass
    return
    
def create_mailing_lists(session_info, provider_addresses): #make mailing lists for each label
    #TODO: fine-tune cases
    #TODO: output as CSV
    mailing_lists = {label: set([]) for label in session_info.keys()}
    mailing_lists["no_emails"] = set([])
    for label in session_info.keys():
        label_dict = session_info[label]
        for number in label_dict.keys():
            mailing_lists[label].update(label_dict[number])
            if number != "from_emails" and len(label_dict[number]) == 0:
                mailing_lists["no_emails"].add(number)
            else:
                mailing_lists["no_emails"].discard(number)
    mailing_lists = {list(mailing_lists[label]) for label in mailing_lists.keys()}
    mailing_lists["no_emails"] = [provider_addresses[number] for number in mailing_lists["no_emails"]]
    return mailing_lists
                
    

 

