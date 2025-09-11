import json
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 简化认证，不使用bcrypt
security = HTTPBearer()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 用户数据文件
USERS_FILE = "users.json"

def load_users():
    """从文件加载用户数据"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # 如果文件不存在或读取失败，返回默认用户
    default_users = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "password": "admin123",
            "created_at": "2024-01-01 10:00:00"
        },
        "analyst": {
            "id": 2,
            "username": "analyst",
            "email": "analyst@example.com",
            "role": "user",
            "password": "analyst123",
            "created_at": "2024-01-02 11:30:00"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users_db):
    """保存用户数据到文件"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

# 加载用户数据库
fake_users_db = load_users()

def verify_password(plain_password: str, stored_password: str) -> bool:
    """验证密码"""
    return plain_password == stored_password

def get_password_hash(password: str) -> str:
    """生成密码哈希（这里直接返回明文）"""
    return password

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
    if not verify_password(password, user["password"]):
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
        global fake_users_db
        
        if username in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_id = max([user["id"] for user in fake_users_db.values()]) + 1
        
        fake_users_db[username] = {
            "id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "password": password,  # 存储明文密码
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存到文件
        save_users(fake_users_db)
        
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
        global fake_users_db
        
        for username, user_data in fake_users_db.items():
            if user_data["id"] == user_id:
                if email:
                    user_data["email"] = email
                if role:
                    user_data["role"] = role
                
                # 保存到文件
                save_users(fake_users_db)
                
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
        global fake_users_db
        
        for username, user_data in fake_users_db.items():
            if user_data["id"] == user_id:
                if username == "admin":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot delete admin user"
                    )
                del fake_users_db[username]
                
                # 保存到文件
                save_users(fake_users_db)
                
                return {"message": "User deleted successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )