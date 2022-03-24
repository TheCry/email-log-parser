#!/usr/bin/python3

import os
import smtplib
import subprocess
import textwrap
import datetime

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

absolutPathOfScript = os.path.dirname(__file__)

# Show output on console
showDebug = 0
# Choose between german (de) or us (us) date format
dateTimeFormat = 'de'
# Minutes how often the cron job is running
cronJobRuntime = 15
# Path of the logfile (Example: /var/log/mail.info)
logFile = ''
# Path of the temp logfile (Example: /var/tmp/mail-info-temp.log)
logFileTemp = ''
# Pattern which you want to find. Example: SPF fail - not authorized
logQueryPattern = ''
# FQDN of your mail server
mailServer = 'your-mailserver.domain.tld'
# SMTP server port
mailServerSmtpPort = 587
# SMTP Username
smtpUsername = ''
# SMTP password
smtpPassword = ''
# Email address of the sender
emailSender = 'sender@domain.tld'
# Email address of the receiver (multiple receivers separate with |)
emailRecipients = 'receiver@domain.tld'
# Email subject
emailSubject = 'This is the subject of the email!'
# Path of the Nagios plugin binary check_log
checkLogBinary = '/usr/lib/nagios/plugins/check_log'

logMessage = ''

today = datetime.datetime.today()
minutesBefore = today - datetime.timedelta(minutes=cronJobRuntime)

if dateTimeFormat == 'de':
    todayDate = today.strftime('%d.%m.%Y')
    todayTime = today.strftime('%H:%M')
    todayTimeBefore = minutesBefore.strftime('%H:%M')
elif dateTimeFormat == 'us':
    todayDate = today.strftime('%Y-%m-%d')
    todayTime = today.strftime('%H:%M %p')
    todayTimeBefore = minutesBefore.strftime('%H:%M %p')
else:
    print('Variable "dateTimeFormat" does not support => ' + str(dateTimeFormat))
    exit(2)

def sendEmail(mailServer,mailServerSmtpPort,smtpUsername,smtpPassword,emailSender,emailRecipients,emailSubject,logMessage):
    emailRecipient = emailRecipients.split("|")
    msg = MIMEMultipart()
    msg['From'] = emailSender
    msg['To'] = ", ".join(emailRecipient)
    msg['Subject'] = emailSubject

    emailMessage = """Your pattern was found!
            \nServer support\n\nFound on """ + str(todayDate) + """ between """ + str(todayTime) + """ - """ + str(todayTimeBefore) + """:\n"""

    if logMessage != '':
        emailMessage += logMessage
    else:
        emailMessage += 'Logparser returns no output!'

    emailMessage = textwrap.dedent(emailMessage).strip()
    msg.attach(MIMEText(emailMessage, 'plain'))

    try:
        server = smtplib.SMTP(mailServer, mailServerSmtpPort)
        server.ehlo()
        server.starttls()
        server.login(smtpUsername, smtpPassword)
        text = msg.as_string()
        server.sendmail(emailSender, emailRecipient, text)
        server.quit()
    except smtplib.SMTPException as error:
        if showDebug:
            print('SMTP server connection error: ' + str(error))
        exit(2)

    return True

if __name__ == '__main__':
    if showDebug:
        print('Start "check_log"')
    checkLogfile = subprocess.run(
        [checkLogBinary, '-F', logFile, '-O', logFileTemp, '-q',
         logQueryPattern], stdout=subprocess.PIPE)
    logCheckReturnCode = checkLogfile.returncode
    logMessage = checkLogfile.stdout.decode('utf-8')

    if showDebug:
        print('Return-code of the Nagios plugin: ' + str(logCheckReturnCode))
        print('Output of the Nagios plugin: ' + str(logMessage))

    if logCheckReturnCode > 0:
        sendEmail(mailServer,mailServerSmtpPort,smtpUsername,smtpPassword,emailSender,emailRecipients,emailSubject,logMessage)
