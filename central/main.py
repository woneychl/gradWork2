import asyncio
import httpx
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import database  # models.py와 database.py가 같은 폴더에 있어야 함

app = FastAPI()

# 서버 시작 시 DB 테이블 생성 (이미 있으면 건너뜀)
models.Base.metadata.create_all(bind=database.engine)

# DB 세션 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 각 은행 서버의 주소 (포트 번호 확인!)
BANK_URLS = {
    "국민은행": "http://127.0.0.1:8001/accounts",
    "하나은행": "http://127.0.0.1:8002/accounts",
    "누리은행": "http://127.0.0.1:8003/accounts"
}

async def fetch_bank_data(client, bank_name, url, user_id):
    """각 은행 서버에 비동기 요청을 보내는 헬퍼 함수"""
    try:
        # 계좌와 카드 API를 각각 호출
        acc_task = client.get(f"{url}/accounts/{user_id}")
        card_task = client.get(f"{url}/cards/{user_id}") # 은행 서버에 /cards/{id}가 있어야 함
        
        acc_res, card_res = await asyncio.gather(acc_task, card_task)
        
        return {
            "bank": bank_name,
            "accounts": acc_res.json() if acc_res.status_code == 200 else [],
            "cards": card_res.json() if card_res.status_code == 200 else [],
            "status": "success"
        }
    except Exception as e:
        return {"bank": bank_name, "status": "error", "error": str(e)}
    


@app.get("/integrated-assets/{user_email}")
async def get_all_assets(user_email: str, db: Session = Depends(get_db)):
    # 1. 중앙 DB에서 이메일로 유저를 찾아 공통 UUID(user_id)를 가져옵니다.
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 이메일로 가입된 사용자가 없습니다.")
    
    target_uuid = str(user.user_id)

    async with httpx.AsyncClient() as client:
        # 2. 모든 은행 서버에 동시에 요청을 보냅니다.
        tasks = [
            fetch_bank_data(client, name, url, target_uuid)
            for name, url in BANK_URLS.items()
        ]
        
        # 3. 모든 응답을 기다립니다.
        responses = await asyncio.gather(*tasks)
        
        # 4. 결과 통합 로직
        total_balance = 0
        all_accounts = []
        all_cards = []
        
        for res in responses:
            if res.get("status") == "success":
                for acc in res["data"]:
                    # 잔액 합산 및 은행 출처 표기
                    total_balance += acc.get("balance", 0)
                    acc["bank_origin"] = res["bank"]
                    all_accounts.append(acc)
                # 카드 정리
                for card in res["cards"]:
                    card["bank_origin"] = res["bank"]
                    all_cards.append(card)

    return {
        "user_name": user.username,
        "user_email": user.email,
        "total_balance": total_balance,
        "account_count": len(all_accounts),
        "card_count": len(all_cards),
        "details": all_accounts,
        "cards": all_cards,
        "debug_info": responses  # 어떤 은행이 성공/실패했는지 확인용
    }