# from . import auth, mail1
# from .models import User
# from itsdangerous import URLSafeTimedSerializer
# from flask_mail import Mail, Message



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(auth.config['SECRET_KEY'])
    return serializer.dumps(email, salt=auth.config['SECURITY_PASSWORD_SALT'])



def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(auth.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=auth.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email



def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=auth.config['MAIL_DEFAULT_SENDER']
    )
    mail1.send(msg)