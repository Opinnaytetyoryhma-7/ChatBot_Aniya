from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_user_by_id
import smtplib
from email.mime.text import MIMEText
from decouple import config

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    user = get_user_by_id(data["sub"]).data[0]
    to_encode.update({"admin": user.get("admin", False)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_res = get_user_by_id(user_id)
    if not user_res.data:
        raise credentials_exception
    user = user_res.data[0]
    return user

def require_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("admin") != True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ei oikeuksia",
        )
    return current_user

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config('SMTP_FROM_EMAIL')
    msg['To'] = to_email
    
    with smtplib.SMTP(config('SMTP_SERVER'), config('SMTP_PORT')) as server:
        server.login(config('SMTP_USERNAME'), config('SMTP_PASSWORD'))
        server.send_message(msg)