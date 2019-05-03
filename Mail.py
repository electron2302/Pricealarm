import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

with open('config.json', 'r') as f:
    config = json.load(f)

config = config['mail']

def sendMail(subject,msg):

    SMTP_host = config['SMTP_host']
    SMTP_port = config['SMTP_port']
    SMTP_user = config['SMTP_user']
    SMTP_password = config['SMTP_password']
    to = config['to']
    
    mail = MIMEMultipart('alternative')
    mail['Subject'] = subject
    mail['From'] = SMTP_user
    mail['To'] = to

    text = config['Frame']['Text'].format(msg=msg)
    html = config['Frame']['HTML'].format(msg=msg)

    mail.attach(MIMEText(text, 'plain'))
    mail.attach(MIMEText(html, 'html'))

    try:  
        if config['ssl']:
            server = smtplib.SMTP_SSL(host=SMTP_host, port=SMTP_port)
        else:
            server = smtplib.SMTP(host=SMTP_host, port=SMTP_port)
        server.ehlo()
        server.login(SMTP_user, SMTP_password)
        server.sendmail(SMTP_user, to, mail.as_string())
        server.close()
        print("Email sent!")
    except:  
        print("Something went wrong while sending the Email...")