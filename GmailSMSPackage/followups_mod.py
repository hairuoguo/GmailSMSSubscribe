import label_threads_mod as lt
import credentials_mod as cm
from apiclient import errors

def ask_for_email(session_info, provider_addresses): #ask emails from all numbers that didn't have any
    for 

 
def send_emails_to_all(email_list, subject, text):
    service = cm.create_service()
    user_id = 'me'
    for email_address in email_list:
        email_message = lt.createMessage(email_address, subject, text)
        try:
            message_result = service.users().messages().send(userId=user_id, body=email_message).execute()
        except errors.HttpError, error:
            print(error)
            continue
    print(message_result)
    return
