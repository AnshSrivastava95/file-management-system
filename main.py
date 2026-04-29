from fastapi import FastAPI,Depends,HTTPException
from database import engine
from model import Base
from schema import UserRegister, UserLogin, OTPVerify,FileRequest
from sqlalchemy.orm import Session
from database import get_db
from auth import register, login, verify_otp
from file_service import create_file, read_file, delete_file
from fastapi.middleware.cors import CORSMiddleware
from auth import get_user_from_session
from crud import get_user_by_email
Base.metadata.create_all(bind=engine)
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/file/list")
def list_files_api(req: dict):
    import os

    files = []
    for file in os.listdir():
        if file.endswith(".txt"):
            files.append(file.replace(".txt", ""))

    return {"files": files}

@app.post("/admin/set-role")
def set_role(data: dict, db: Session = Depends(get_db)):
    session = data.get("session")
    target_email = data.get("email")
    new_role = data.get("role")

    current_user = get_user_from_session(session, db)

    if not current_user or current_user.role != "superadmin":
        raise HTTPException(403, "Not authorized")

    user = get_user_by_email(db, target_email)
    if not user:
        raise HTTPException(404, "User not found")

    user.role = new_role
    db.commit()

    return {"message": f"{target_email} is now {new_role}"}

@app.post("/me")
@app.post("/me")
def get_me(data: dict, db: Session = Depends(get_db)):
    session_id = data.get("session")

    user = get_user_from_session(session_id, db)

    if not user:
        return {"error": "Invalid session"}

    return {"email": user.email, "role": user.role}