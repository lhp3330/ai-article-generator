"""用户路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Response
from databases import Database

from app.database import get_db
from app.schemas.common import BaseResponse, DeleteRequest
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserAddRequest,
    UserUpdateRequest, UserQueryRequest, UserVO, LoginUserVO
)
from app.services.user_service import UserService
from app.deps import get_current_user, require_login, require_admin, generate_session_id
from app.utils.session import set_session, remove_session
from app.config import settings

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/register", response_model=BaseResponse[int])
async def register(
        request: UserRegisterRequest,
        db: Database = Depends(get_db)
):
    """用户注册"""
    service = UserService(db)
    user_id = await service.register(request)
    return BaseResponse.success(data=user_id, message="注册成功")


@router.post("/login", response_model=BaseResponse[LoginUserVO])
async def login(
        request: UserLoginRequest,
        response: Response,
        db: Database = Depends(get_db)
):
    """用户登录"""
    service = UserService(db)
    user = await service.login(request)

    # 生成 Session ID
    session_id = generate_session_id()

    # 保存到 Redis
    await set_session(session_id, {"user": user.model_dump(by_alias=True)})

    # 设置 Cookie
    response.set_cookie(
        key="SESSION",
        value=session_id,
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax"
    )

    return BaseResponse.success(data=user, message="登录成功")
