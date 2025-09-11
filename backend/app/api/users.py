from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from app.models.schemas import User, UserCreate, UserUpdate, LoginRequest, Token
from app.services.auth_service import (
    authenticate_user, create_access_token, get_current_user, 
    require_admin, UserService, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """用户登录"""
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": current_user["created_at"]
    }

@router.get("/users")
async def get_users(current_user: dict = Depends(require_admin)):
    """获取用户列表（需要管理员权限）"""
    try:
        users = UserService.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_admin)
):
    """创建新用户（需要管理员权限）"""
    try:
        new_user = UserService.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(require_admin)
):
    """更新用户信息（需要管理员权限）"""
    try:
        updated_user = UserService.update_user(
            user_id=user_id,
            email=user_data.email,
            role=user_data.role
        )
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_admin)
):
    """删除用户（需要管理员权限）"""
    try:
        result = UserService.delete_user(user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取特定用户信息"""
    # 普通用户只能查看自己的信息，管理员可以查看所有用户
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="没有权限访问此用户信息"
        )
    
    try:
        users = UserService.get_all_users()
        for user in users:
            if user["id"] == user_id:
                return user
        
        raise HTTPException(status_code=404, detail="用户不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")