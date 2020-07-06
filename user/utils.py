import secrets

from django.core.mail import send_mail  # 发送邮件

from douban.settings import EMAIL_FROM


def send_code_email(email, email_title, email_body):
    send_mail(email_title, email_body, EMAIL_FROM, [email])


def gen_code():
    return "".join([str(secrets.randbelow(10)) for i in range(6)])
