from database import conf  # database.py에 설정한 메일 설정(conf)을 가져오기
import asyncio, httpx, random
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import FastMail, MessageSchema 
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware

import models
import database 
import Security

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 모든 접속 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT 토큰을 추출하기 위한 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# DB 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

# DB 세션 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic 모델: 클라이언트로부터 받을 데이터 구조 정의
class UserCreate(BaseModel):
    email: EmailStr  # 이메일 형식을 자동으로 검증함
    password: str
    username: str
    phone_number: str 

pending_users = {}

@app.post("/signup", status_code=status.HTTP_200_OK) # 저장 전이므로 200으로 변경
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. 실제 DB에 이미 가입된 이메일인지 확인
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    # 2. 6자리 인증번호 생성
    verification_code = str(random.randint(100000, 999999))

    # 3. [핵심] DB 저장 대신 메모리에 임시 저장
    # 나중에 verify에서 꺼내 쓸 수 있도록 가입 정보를 통째로 보관합니다.
    pending_users[user_in.email] = {
        "user_in": user_in,
        "code": verification_code
    }

    # 4. 이메일 발송
    try:
        message = MessageSchema(
            subject="Toss Clone 회원가입 인증번호",
            recipients=[user_in.email],
            body=f"안녕하세요! 인증번호는 [{verification_code}] 입니다.",
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)

        return {"message": "인증 메일이 발송되었습니다."}
    except Exception as e:
        # 메일 발송 실패 시 임시 저장 데이터 삭제
        if user_in.email in pending_users:
            del pending_users[user_in.email]
        raise HTTPException(status_code=500, detail=f"메일 발송 오류: {str(e)}")
    
class VerifyRequest(BaseModel):
    email: str
    code: str

@app.post("/verify", status_code=200)
async def verify_email(data: VerifyRequest, db: Session = Depends(get_db)):
    # 1. 임시 저장소에서 해당 이메일 정보 찾기
    temp_data = pending_users.get(data.email)

    if not temp_data:
        raise HTTPException(status_code=400, detail="인증 세션이 만료되었거나 가입 요청이 없습니다.")
    
    stored_code = str(temp_data["code"]).strip()
    input_code = str(data.code).strip()

    if stored_code == input_code: #번호가 맞으면 비로소 실제 DB에 저장
        user_in = temp_data["user_in"]
        hashed_pw = Security.get_password_hash(user_in.password)
        
        new_user = models.User(
            email=user_in.email,
            hashed_password=hashed_pw,
            username=user_in.username,
            phone_number=user_in.phone_number,     
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        del pending_users[data.email] # 가입 성공했으므로 임시 데이터 삭제
        
        access_token = Security.create_access_token(data={"sub": new_user.email})
        return {
            "message": "회원가입이 최종 완료되었습니다.",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": new_user.user_id
        }

        
    else:
        raise HTTPException(status_code=400, detail="인증번호가 일치하지 않습니다.")

# --- 실제 로그인 API ---
@app.post("/login")
async def login(login_data: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data["email"]).first()
    if not user or not Security.verify_password(login_data["password"], user.hashed_password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다.")
    
    access_token = Security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 추가된 인증 헬퍼 함수 ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """토큰을 검증하고 현재 로그인한 유저 객체를 반환"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명을 확인하지 못했습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Security.SECRET_KEY, algorithms=[Security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


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
    


@app.get("/integrated-assets") 
async def get_all_assets(
    current_user: models.User = Depends(get_current_user), # 토큰으로 유저 확인
    db: Session = Depends(get_db)
):
    target_uuid = str(current_user.user.user_id)

    async with httpx.AsyncClient() as client:
        # 모든 은행 서버에 동시에 요청을 보냅니다.
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
                for acc in res["accounts"]:
                    # 잔액 합산 및 은행 출처 표기
                    total_balance += acc.get("balance", 0)
                    acc["bank_origin"] = res["bank"]
                    all_accounts.append(acc)
                # 카드 정리
                for card in res["cards"]:
                    card["bank_origin"] = res["bank"]
                    all_cards.append(card)

    return {
        "user_name": current_user.username,
        "user_email": current_user.email,
        "total_balance": total_balance,
        "account_count": len(all_accounts),
        "card_count": len(all_cards),
        "details": all_accounts,
        "cards": all_cards
    }

