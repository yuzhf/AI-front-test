from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # admin123
        "created_at": "2024-01-01 10:00:00"
    },
    "analyst": {
        "id": 2,
        "username": "analyst",
        "email": "analyst@example.com",
        "role": "user",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # analyst123
        "created_at": "2024-01-02 11:30:00"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def get_user(username: str):
    """获取用户信息"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None

def authenticate_user(username: str, password: str):
    """验证用户身份"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT令牌"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

def get_current_user(user: dict = Depends(verify_token)):
    """获取当前用户"""
    return user

def require_admin(user: dict = Depends(get_current_user)):
    """要求管理员权限"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

class UserService:
    @staticmethod
    def get_all_users():
        """获取所有用户"""
        return [
            {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "role": user_data["role"],
                "created_at": user_data["created_at"]
            }
            for user_data in fake_users_db.values()
        ]
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = "user"):
        """创建用户"""
        if username in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_id = max([user["id"] for user in fake_users_db.values()]) + 1
        hashed_password = get_password_hash(password)
        
        fake_users_db[username] = {
            "id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "hashed_password": hashed_password,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "created_at": fake_users_db[username]["created_at"]
        }
    
    @staticmethod
    def update_user(user_id: int, email: str = None, role: str = None):
        """更新用户"""
        for username, user_data in fake_users_db.items():
            if user_data["id"] == user_id:
                if email:
                    user_data["email"] = email
                if role:
                    user_data["role"] = role
                
                return {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "role": user_data["role"],
                    "created_at": user_data["created_at"]
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    @staticmethod
    def delete_user(user_id: int):
        """删除用户"""
        for username, user_data in fake_users_db.items():
            if user_data["id"] == user_id:
                if username == "admin":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot delete admin user"
                    )
                del fake_users_db[username]
                return {"message": "User deleted successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )