__author__ = 'asherkhb'

from cPickle import load
from myCoGe import final_cleanup, send_email_log

downloads = load(open('./temp/finalize_downloads.p', 'rb'))
email_log_attachments = load(open('./temp/finalize_email_log_attachments.p', 'rb'))

send_email_log(downloads, email_log_attachments)

final_cleanup()