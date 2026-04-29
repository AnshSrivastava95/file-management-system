from sqlalchemy.orm import Session
from auth import get_user_from_session
from cryptography.fernet import Fernet
import os

KEY = b'ryJwiN2S8eeYQepVmar-ayaZiYcFCblR6lKLLNNBwnk='
cipher = Fernet(KEY)

def validate_filename(filename: str):
    return filename.isalnum() and len(filename) <= 50

def validate_content(content: str):
    return len(content) <= 1000


def log_event(message: str):
    with open("logs.txt", "a") as f:
        f.write(message + "\n")


def check_permission(role: str, action: str):
    permissions = {
        "admin": ["read", "write", "delete"],
        "user": ["read", "write"]
    }
    return action in permissions.get(role, [])



def create_file(session_id: str, filename: str, content: str, db: Session):
    user = get_user_from_session(session_id, db)

    if not user:
        return {"error": "Invalid session"}

    if not validate_filename(filename) or not validate_content(content):
        return {"error": "Invalid input"}

    if not check_permission(user.role, "write"):
        log_event(f"{user.email} unauthorized write attempt")
        return {"error": "Permission denied"}

    encrypted = cipher.encrypt(content.encode())

    with open(f"{filename}.txt", "wb") as f:
        f.write(encrypted)

    return {"message": "File created securely"}


def read_file(session_id: str, filename: str, db: Session):
    user = get_user_from_session(session_id, db)

    if not user:
        return {"error": "Invalid session"}

    if not validate_filename(filename):
        return {"error": "Invalid filename"}

    if not check_permission(user.role, "read"):
        log_event(f"{user.email} unauthorized read attempt")
        return {"error": "Permission denied"}

    if not os.path.exists(f"{filename}.txt"):
        return {"error": "File not found"}

    with open(f"{filename}.txt", "rb") as f:
        encrypted = f.read()

    decrypted = cipher.decrypt(encrypted).decode()

    return {"content": decrypted}


def delete_file(session_id: str, filename: str, db: Session):
    user = get_user_from_session(session_id, db)

    if not user:
        return {"error": "Invalid session"}

    if not validate_filename(filename):
        return {"error": "Invalid filename"}

    if not check_permission(user.role, "delete"):
        log_event(f"{user.email} unauthorized delete attempt")
        return {"error": "Permission denied"}

    file_path = f"{filename}.txt"

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    os.remove(file_path)

    return {"message": "File deleted successfully"}