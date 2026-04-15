from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    # 모든 서버가 공유할 고유 식별자
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # 로그인용
    username = Column(String)
    is_active = Column(Boolean, default=True)

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"))
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 계좌번호로 직접 조회하기 위해 from_account를 사용합니다.
    from_account = Column(String, nullable=False)
    to_account = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String) 
    category = Column(String) 
    description = Column(String)
    # DB의 created_at과 매핑됩니다.
    created_at = Column(TIMESTAMP(timezone=True))