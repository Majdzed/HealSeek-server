import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.utils.template_creator import create_html_template


def send_mail(receiver : str , subject : str, message_context : str , subheading : str = ""):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = settings.MY_MAIL  # Enter your address
    password =  settings.MY_PASS

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = "HealSeak"
    message["To"] = receiver
    text = """\
    Hi,
    How are you?"""


    html_context = create_html_template(message_context, subheading)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html_context, "html")

    message.attach(part1)
    message.attach(part2)


    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            print(server.sendmail(sender_email, receiver, message.as_string()))
    except  Exception as e: 
        print(str(e))