from __future__ import print_function
import os
import threading
import time
import Queue
from datetime import datetime
from apiclient import errors
from apiclient import discovery
from oauth2client import client
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import csv
import credentials_mod as cm

class getEmails(threading.Thread):
    
    def __init__(self, label_id, label_name, queue, lock, freq):
        threading.Thread.__init__(self)
        self.service = cm.create_service()
        self.threadID = label_id + '_get'
        self.label_id = label_id
        self.label_name = label_name
        self.q = queue
        self.q_lock = lock
        self.freq = freq
        self.counter = 0

    
    def run(self):
        print('Starting subscription acquiring thread for %s.\n' % (self.label_name,))
        start_time = time.time()
        prev_log_time = 0
        while True:
            time.sleep(self.freq - (time.time() - start_time) % self.freq)
            new_counts = get_new_message_ids(self.service, self.q, self.label_id, self.q_lock)
            self.counter += new_counts
            if new_counts > 0:
                print('%s: %s subscriptions total received for %s' % (datetime.now(), self.counter, self.label_name))



class sendResponses(threading.Thread):
    
    def __init__(self, label_id, label_name, queue, lock, freq):
        threading.Thread.__init__(self)
        self.service = cm.create_service()
        self.threadID = label_id + 'respond'
        self.label_id = label_id
        self.label_name = label_name
        self.q = queue
        self.q_lock = lock
        self.freq = freq
        self.counter = 0

    
    def run(self):
        print('Starting subscription confirming thread for %s.\n' % (self.label_name,))
        start_time = time.time()
        prev_log_time = 0
        while True:
            time.sleep(self.freq - (time.time() - start_time) % self.freq)
            new_counts = send_responses(self.service, self.q, self.label_id, self.label_name, self.q_lock)
            self.counter += new_counts
            if new_counts > 0:
                print('%s: %s subscriptions total confirmed for %s' % (datetime.now(), self.counter, self.label_name))



def get_new_message_ids(service, message_queue, label_id, lock):
    user_id = 'me'
    list_query = 'is:unread'
    
    try:
        result_ids = cm.get_message_ids(service, label_id, list_query)
        for message_id in result_ids:
            msg_labels = {
                'removeLabelIds': [
                    'UNREAD'] }
            service.users().messages().modify(userId = user_id, id = message_id, body = msg_labels).execute()
            lock.acquire()
            message_queue.add(message_id)
            lock.release()
        
        return len(result_ids)
    except errors.HttpError:
        error = None
        print(error)
        pass
    return 0


def send_responses(service, message_queue, label_id, label_name, lock):
    user_id = 'me'
    message_format = 'metadata'
    messages_handled = set([])
    lock.acquire()
    for message in message_queue:
        
        try:
            message_data = service.users().messages().get(userId = user_id, id = message, format = message_format).execute()
            from_address = filter((lambda x: x['name'] == 'From'), message_data['payload']['headers'])[0]
            address = from_address['value']
            if label_name == 'INBOX':
                confirmation_message = createMessage(address, '[DofA] Invalid code', 'The session code that you entered was invalid. Please check and try again. Examples of valid codes are "ACT" and session codes such as "DoA01", "DoA32.5", and "DoA100"')
            elif label_name == 'ACT':
                confirmation_message = createMessage(address, '[DofA] Confirmation', 'Thank you for subscribing to follow-ups about the Day of Action!')
            else:
                confirmation_message = createMessage(address, '[DofA] Confirmation', 'Thank you for subscribing to updates for the topics covered in session: ' + label_name + '.')
            message_result = service.users().messages().send(userId = user_id, body = confirmation_message).execute()
            messages_handled.add(message)
        continue
        except errors.HttpError:
            error = None
            print(error)
            continue
    message_queue.difference_update(messages_handled)
    lock.release()
    if len(messages_handled) > 0:
        return len(messages_handled)
    return 0


def createMessage(to, subject, text):
    message = MIMEText(text)
    message['to'] = to
    message['from'] = 'mitdayofaction@gmail.com'
    message['subject'] = subject
    return {
        'raw': base64.urlsafe_b64encode(message.as_string()) }


def get_label_ids(label_names):
    service = cm.create_service()
    label_ids = []
    label_ids_to_names = { }
    new_labels = label_names[:]
    
    try:
        label_data = service.users().labels().list(userId = 'me').execute()
        label_list = label_data['labels']
        for label in label_list:
            if label['name'] in label_names:
                label_ids_to_names[label['id']] = label['name']
                label_ids.append(label['id'])
                new_labels.remove(label['name'])
        for new_label in new_labels:
            label_object = {
                'messsageListVisilibity': 'show',
                'name': new_label,
                'labelListVisibility': 'labelShow' }
            result = service.users().labels().create(userId = 'me', body = label_object).execute()
            label_ids_to_names[result['id']] = new_label
            label_ids.append(result['id'])
            print('Created label %s' % (new_label,))
    except errors.HttpError:
        error = None
        print(error)
    return (label_ids, label_ids_to_names)


def import_labels_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        label_list = list(reader)
        label_list = [ label[0] for label in label_list ]
    return label_list

