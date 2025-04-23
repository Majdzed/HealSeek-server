import pyotp
from app.config import settings
from app.utils.mail_sender import send_mail
key = settings.TWOFACTOR_SECRET

def generate_2fa_code(receiver : str):
    topt = pyotp.TOTP(key)
    code = topt.now()
    send_mail(receiver=receiver , subject="2FA code" , message_context="Your 2FA code is " , subheading=code.__str__())

def verify_2fa_code(code):
    topt = pyotp.TOTP(key)
    print(code)
    print(topt.now())
    return topt.verify(code)