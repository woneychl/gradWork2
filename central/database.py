from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ 본인의 PostgreSQL 비밀번호와 DB 이름으로 수정하세요!
# 형식: postgresql://[사용자]:[비밀번호]@[주소]:[포트]/[DB이름]
KUKMIN_DATABASE_URL = "postgresql://postgres:kdu21240@bankdb.c12yak4o0wk1.ap-northeast-2.rds.amazonaws.com:5432/kukmin"

engine = create_engine(KUKMIN_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()