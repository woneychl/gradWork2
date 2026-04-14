from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import database

app = FastAPI()

# DB 세션을 여닫는 함수
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/accounts/{target_user_id}")
def get_user_accounts(target_user_id: str, db: Session = Depends(get_db)):
    # SQL의 "SELECT * FROM accounts WHERE user_id = '...';"과 같습니다.
    accounts = db.query(models.Account).filter(models.Account.user_id == target_user_id).all()
    
    if not accounts:
        return {"message": "이 유저의 계좌가 없습니다."}
        
    return accounts

@app.get("/accounts/{acc_num}")
def get_specific_account(acc_num: str, db: Session = Depends(get_db)):
    # 특정 계좌번호로 조회
    account = db.query(models.Account).filter(models.Account.account_number == acc_num).first()
    if not account:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다.")
    return account

@app.get("/transactions")
def get_all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    return transactions