import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

# 1. .env 파일의 환경 변수를 읽어옵니다.
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

# 2. RDS 연결 주소를 가져옵니다.
# .env 파일
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")

# 3. DB 엔진 생성
# 만약 URL을 못 읽어오면 에러가 나므로, None 체크를 하면 좋습니다.
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DB_URL이 .env 파일에 설정되지 않았습니다.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. DB와 대화하기 위한 세션 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 모델들이 상속받을 기본 클래스
Base = declarative_base()