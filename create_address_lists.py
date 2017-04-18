import GmailSMSPackage.format_data_mod as fd
import GmailSMSPackage.label_threads_mod as lt

def main():
    label_names = ['INBOX', 'ACT', 'ADD_EMAIL']
    session_codes = ['#' + code for code in lt.import_labels_csv('session_codes.csv')]
    label_names += session_codes
    session_info, provider_addresses = fd.format_session_info(label_names)
    headcount = fd.get_total_headcount(session_info)
    print(headcount)
    return
    
if __name__ == "__main__":
    main()
