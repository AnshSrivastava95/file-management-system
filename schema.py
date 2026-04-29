from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class OTPVerify(BaseModel):
    email: str
    otp: str
    

class FileRequest(BaseModel):
    session: str
    filename: str
    content: str = ""