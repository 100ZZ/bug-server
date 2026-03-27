"""认证相关工具函数"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib

# JWT 配置
SECRET_KEY = "your-secret-key-here-change-in-production"  # 生产环境应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时


def hash_password(password: str) -> str:
    """
    加密密码
    
    Args:
        password: 明文密码
    
    Returns:
        加密后的密码
    """
    # bcrypt 限制密码最多 72 字节
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码
    
    Returns:
        是否匹配
    """
    # bcrypt 限制密码最多 72 字节
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间
    
    Returns:
        JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码访问令牌
    
    Args:
        token: JWT token
    
    Returns:
        解码后的数据，如果失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """当前用户信息"""
    id: int
    username: str
    role: str


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """
    获取当前登录用户
    
    Args:
        credentials: HTTP Bearer 凭证
    
    Returns:
        当前用户信息
    
    Raises:
        HTTPException: 如果认证失败
    """
    # 未提供认证信息是正常情况（未登录），不需要日志输出
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")
    
    if user_id is None or username is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌格式错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUser(id=int(user_id), username=username, role=role)

