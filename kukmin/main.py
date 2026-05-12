from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import database

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. 앱 메인용: 은행 전체 상품 및 프로모션 (Public)
@app.get("/bank/marketing")
def get_bank_marketing_info(db: Session = Depends(get_db)):
    # 중앙 서버가 앱 메인 화면을 구성할 때 호출
    cards = db.query(models.Card).all()
    promotions = db.query(models.Promotion).filter(models.Promotion.is_active == True).all()
    
    return {
        "bank_name": "kukmin", 
        "available_cards": cards,
        "active_promotions": promotions
    }

# 2. 자산 관리용: 특정 유저의 통합 데이터 (Private)
@app.get("/user/assets/{email}")
def get_user_integrated_assets(email: str, db: Session = Depends(get_db)):
    # 1. User 테이블에서 이메일로 유저를 먼저 찾습니다.
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 이메일의 사용자를 찾을 수 없습니다.")
    accounts = db.query(models.Account).filter(models.Account.user_id == user.user_id).all()
    all_cards = []
    all_transactions = []

    for acc in accounts:
        all_cards.extend(acc.cards)
        
    if not all_transactions:
        account_ids = [acc.account_id for acc in accounts]
        all_transactions = db.query(models.Transaction).filter(
            models.Transaction.account_id.in_(account_ids)
        ).order_by(models.Transaction.created_at.desc()).limit(30).all()

    return {
        "bank": "kukmin",
        "user_name": user.username,
        "accounts": accounts,
        "my_cards": all_cards,
        "transactions": all_transactions
    }