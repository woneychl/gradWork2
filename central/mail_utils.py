# mail_utils.py (이메일 발송 유틸)
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME = "woneychl@gmail.com",
    MAIL_PASSWORD = "snbl akvr lzio mpey", # 구글 앱 비밀번호
    MAIL_FROM = "woneychl@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_verification_email(email: EmailStr, code: str):
    message = MessageSchema(
        subject="[Toss Clone] 회원가입 인증번호입니다",
        recipients=[email],
        body=f"인증번호 6자리는 [{code}] 입니다.",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)