import threading
import GmailSMSPackage
import GmailSMSPackage.label_threads_mod as lt
import GmailSMSPackage.credentials_mod as cm
import time
from datetime import datetime
 
def main():
    label_names = ['INBOX', 'ACT', 'ADD_EMAIL']
    session_codes = ['#' + code for code in lt.import_labels_csv('session_codes.csv')]
    label_names += session_codes
    
    label_ids, label_ids_to_names = lt.get_label_ids(label_names)
    
    for label_id in label_ids:
        label_name = label_ids_to_names[label_id]
        label_queue = set([])
        queue_lock = threading.Lock()
        update_thread = lt.getEmails(label_id, label_name, label_queue, queue_lock, 10.0)
        response_thread = lt.sendResponses(label_id, label_name, label_queue, queue_lock, 10.0)
        update_thread.start()
        response_thread.start()
        prev_log_time = 0
    while True:
        if time.time() - prev_log_time > 60.0:
            print("%s: Still running" % (datetime.now(),))
            prev_log_time = time.time()
    

if __name__ == '__main__':
    main()
