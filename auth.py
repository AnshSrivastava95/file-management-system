from sqlalchemy.orm import Session
import hashlib,random,time
from crud import create_user,get_user_by_email
import uuid
import smtplib
from email.mime.text import MIMEText
sessions={}
EMAIL = "anshsrivastava112006@gmail.com"
APP_PASSWORD = "xqcvncqnuhgcseid"

def send_otp_email(receiver_email, otp):
    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, receiver_email, msg.as_string())

otp_store={}
def hash_password(password:str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password:str,hashed_password:str):
    return hash_password(password)==hashed_password

def generate_otp():
    return str(random.randint(100000,999999))

def register(db:Session,email:str,password:str):
    existing=get_user_by_email(db,email)
    if existing:
        return {"error":"user already exists"}
    user=create_user(db,email,hash_password(password))
    return {"message": "User registered successfully", "user_id": user.id}
    
def login(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user.password):
        return {"error": "Invalid password"}

    otp = generate_otp()
    otp_store[email] = {"otp": otp, "time": time.time()}
    send_otp_email(email, otp) 

    return {"message": "OTP sent to email"}

def get_user_from_session(session_id: str, db: Session):
    email = sessions.get(session_id)

    if not email:
        return None

    return get_user_by_email(db, email)

def verify_otp(email: str, otp: str):
    data = otp_store.get(email)
    if not data:
        return {"error": "No OTP"}

    if time.time() - data["time"] > 300:
        del otp_store[email]
        return {"error": "OTP expired"}

    if data["otp"] != otp:
        return {"error": "Invalid OTP"}

    del otp_store[email]
    session_id = str(uuid.uuid4())
    sessions[session_id] = email
    return {"message": "Login success",
            "session":session_id
            }
    

    