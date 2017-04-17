import threading
import GmailSMSPackage
import GmailSMSPackage.label_threads_mod as lt
import GmailSMSPackage.credentials_mod as cm
 
def main():
    label_names = ['INBOX', 'DofA1', 'DofA2']
    
    label_ids, label_ids_to_names = lt.get_label_ids(label_names)
    
    for label_id in label_ids:
        label_name = label_ids_to_names[label_id]
        label_queue = set([])
        queue_lock = threading.Lock()
        update_thread = lt.getEmails(label_id, label_name, label_queue, queue_lock, 5.0)
        response_thread = lt.sendResponses(label_id, label_name, label_queue, queue_lock, 5.0)
        update_thread.start()
        response_thread.start()

if __name__ == '__main__':
    main()
