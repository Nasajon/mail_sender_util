import smtplib
from email.mime.text import MIMEText
import ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# initialize connection to our email server, we will use Outlook here
smtp = smtplib.SMTP('smtp-mail.outlook.com', port='587')

smtp.ehlo()  # send the extended hello to our server
smtp.starttls(context=ctx)  # tell server we want to communicate with TLS encryption

smtp.login('sergio.rocha.silva@outlook.com', '151625St#')  # login to our email server

msg = MIMEText('This is test mail')

msg['Subject'] = 'Test mail'
msg['From'] = 'sergio.rocha.silva@outlook.com'
msg['To'] = 'sergiosilva@nasajon.com.br'

# send our email message 'msg' to our boss
smtp.sendmail('sergio.rocha.silva@outlook.com',
              'sergiosilva@nasajon.com.br',
              msg.as_string())
              
smtp.quit() 