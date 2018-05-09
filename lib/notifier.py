import smtplib
from email.mime.text import MIMEText

from settings import mailto_list, mail_host, mail_user, mail_pass, USE_EMAIL


def send_mail(sub, content, to_list=mailto_list):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = mail_user
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False

