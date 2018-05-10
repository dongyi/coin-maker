import smtplib
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from settings import mailto_list, mail_host, mail_user, mail_pass, USE_EMAIL


def send_mail(sub, content, to_list=mailto_list):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = mail_user

    server = SMTP_SSL(mail_host)

    server.login(mail_user, mail_pass)
    server.sendmail(mail_user, to_list, msg.as_string())
    server.quit()
    return True


if __name__ == '__main__':
    send_mail('test_title', 'test_content')