from fastapi import FastAPI,Depends,HTTPException
from database import engine
from model import Base
from schema import UserRegister, UserLogin, OTPVerify,FileRequest
from sqlalchemy.orm import Session
from database import get_db
from auth import register, login, verify_otp
from file_service import create_file, read_file, delete_file
Base.metadata.create_all(bind=engine)


app=FastAPI()

@app.post("/register")
def register_user(u: UserRegister, db: Session = Depends(get_db)):
    r = register(db, u.email, u.password)
    if "error" in r:
        raise HTTPException(400, r["error"])
    return r

@app.post("/login")
def login_user(u: UserLogin, db: Session = Depends(get_db)):
    r = login(db, u.email, u.password)
    if "error" in r:
        raise HTTPException(401, r["error"])
    return r

@app.post("/verify-otp")
def verify_otp_api(u: OTPVerify):
    r = verify_otp(u.email, u.otp)

    if "error" in r:
        raise HTTPException(status_code=401, detail=r["error"])

    return r

@app.post("/file/create")
def create_file_api(req: FileRequest, db: Session = Depends(get_db)):
    r = create_file(req.session, req.filename, req.content, db)

    if "error" in r:
        raise HTTPException(403, r["error"])

    return r

@app.post("/file/read")
def read_file_api(req: FileRequest, db: Session = Depends(get_db)):
    r = read_file(req.session, req.filename, db)

    if "error" in r:
        raise HTTPException(status_code=403, detail=r["error"])

    return r

@app.post("/file/delete")
def delete_file_api(req: FileRequest, db: Session = Depends(get_db)):
    r = delete_file(req.session, req.filename, db)

    if "error" in r:
        raise HTTPException(status_code=403, detail=r["error"])

    return r