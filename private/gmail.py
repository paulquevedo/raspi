#!/usr/bin/python2.7

from argparse import ArgumentParser
from email.mime.text import MIMEText
from smtplib import SMTP
from socket import gethostname

parser = ArgumentParser();
parser.add_argument("toaddr");
parser.add_argument("-s", "--subject", help="message subject");
parser.add_argument("body", help="message body");
args = parser.parse_args();

fromaddr = 'me@gmail.com'
username = 'me@gmail.com'
password = 'password'

if args.subject is not None:
    subject = args.subject
else:
    subject = gethostname() + " Notification"

msg = MIMEText(args.body)
msg['Subject'] = subject
msg['From']    = fromaddr
msg['To']      = args.toaddr

server = SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, args.toaddr, msg.as_string())
server.quit()
