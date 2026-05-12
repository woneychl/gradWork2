from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB,UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String)
    phone_number = Column(String, unique=True, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"))
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    # 추가: 이 계좌와 연결된 카드들을 자동으로 가져오기 위한 설정
    cards = relationship("Users_Cards", back_populates="account")

# 3. 은행 판매용 카드 상품 
class Card(Base):
    __tablename__ = "cards"

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_name = Column(String, nullable=False)
    card_type = Column(String) # 체크/신용
    benefits = Column(String) # 기본 혜택 정보
    limit_amount = Column(Numeric(15, 2)) #일일 한도
    benefits = Column(JSONB)
    is_active = Column(Boolean)

# 4. 가입자가 실제 보유한 카드
class Users_Cards(Base):
    __tablename__ = "users_cards"
    # 외래키 설정: 어떤 계좌와 연결된 카드인지
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE"))
    card_number = Column(String, primary_key=True, nullable=False)
    card_name = Column(String)
    card_type = Column(String)
    cvc = Column(String)
    expiry_date = Column(String)
    limit_amount = Column(Numeric(15, 2))
    benefits = Column(JSONB)
    is_active = Column(Boolean, default=True)

    account = relationship("Account", back_populates="cards")

class Transaction(Base):
    __tablename__ = "users_transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 계좌번호로 직접 조회하기 위해 from_account를 사용합니다.
    from_account = Column(String, nullable=False)
    to_account = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String) 
    category = Column(String) 
    created_at = Column(TIMESTAMP(timezone=True))
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE"))