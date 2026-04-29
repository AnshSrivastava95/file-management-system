from sqlalchemy.orm import Session
from model import user

def create_user(db: Session, email: str, password: str, role: str):
    User = user(email=email, password=password, role=role)
    db.add(User)
    db.commit()
    db.refresh(User)
    return User

def get_user_by_email(db: Session, email: str):
    return db.query(user).filter(user.email == email).first()

def update_user_role(db: Session, email: str, new_role: str):
    User = db.query(user).filter(user.email == email).first()
    if User:
        User.role = new_role
        db.commit()
        db.refresh(User)
    return User

def delete_user(db: Session, email: str):
    User = db.query(user).filter(user.email == email).first()
    if user:
        db.delete(User)
        db.commit()
    return User

def create_file(session_id: str, filename: str, content: str, db: Session):
    user = get_user_from_session(session_id, db)

    if not user:
        return {"error": "Invalid session"}

    if user.role != "admin" and user.role != "user":
        return {"error": "Permission denied"}