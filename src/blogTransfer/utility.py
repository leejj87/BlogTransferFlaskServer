import os
import datetime
log_directory=os.path.join(os.getcwd(),'logs')
def logs_main(msg):
    with open(os.path.join(log_directory,"logs_main.log"),'a') as f:
        f.write(datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')+'\t'+msg+'\n')

def logs_system(msg):
    with open(os.path.join(log_directory,"logs_sys.log"),'a') as f:
        f.write(datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')+'\t'+msg+'\n')


def read_logs(log_file_name):
    if os.path.exists(os.path.join(log_directory,log_file_name)):
        with open(os.path.join(log_directory,log_file_name), 'r') as f:
            lines=f.readlines()
        return lines
    else:
        return []

