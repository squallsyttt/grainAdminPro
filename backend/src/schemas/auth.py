"""
认证相关 Schema
用于登录、token 刷新等认证接口
"""
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    登录请求

    用于管理员和商家登录
    """

    username: str = Field(..., description="用户名（管理员用户名或商家编号）", min_length=3, max_length=100)
    password: str = Field(..., description="密码", min_length=6, max_length=100)

    model_config = {"json_schema_extra": {"example": {"username": "admin", "password": "admin123"}}}


class TokenResponse(BaseModel):
    """
    Token 响应

    返回访问令牌和刷新令牌
    """

    access_token: str = Field(..., description="访问令牌（15分钟有效期）")
    refresh_token: str = Field(..., description="刷新令牌（7天有效期）")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """
    刷新 Token 请求

    使用 refresh_token 换取新的 access_token
    """

    refresh_token: str = Field(..., description="刷新令牌")

    model_config = {
        "json_schema_extra": {"example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}}
    }


class UserInfoResponse(BaseModel):
    """
    用户信息响应

    返回当前登录用户的基本信息
    """

    user_id: str = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    role: str = Field(..., description="用户角色（admin/merchant）")
    merchant_id: Optional[str] = Field(None, description="商家编号（仅商家用户）")
    merchant_name: Optional[str] = Field(None, description="商家名称（仅商家用户）")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "admin",
                "role": "admin",
                "merchant_id": None,
                "merchant_name": None,
            }
        }
    }


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求

    用于商家修改自己的密码
    """

    old_password: str = Field(..., description="旧密码", min_length=6, max_length=100)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=100)

    model_config = {"json_schema_extra": {"example": {"old_password": "old123456", "new_password": "new123456"}}}


class MessageResponse(BaseModel):
    """
    通用消息响应

    用于返回操作结果消息
    """

    message: str = Field(..., description="消息内容")

    model_config = {"json_schema_extra": {"example": {"message": "操作成功"}}}
