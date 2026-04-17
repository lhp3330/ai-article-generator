from operator import and_

from select import select

from sqlalchemy.sql import func
from app.exceptions import throw_if, ErrorCode, throw_if_not
from app.models.user import User
from app.schemas.user import UserRegisterRequest, LoginUserVO, UserLoginRequest
from app.utils.password import encrypt_password


async def register(self, request: UserRegisterRequest) -> int:
    """用户注册"""
    # 校验参数
    throw_if(
        len(request.user_account) < 4,
        ErrorCode.PARAMS_ERROR,
        "账号长度不能小于 4 位"
    )
    throw_if(
        len(request.user_password) < 8,
        ErrorCode.PARAMS_ERROR,
        "密码长度不能小于 8 位"
    )
    throw_if(
        request.user_password != request.check_password,
        ErrorCode.PARAMS_ERROR,
        "两次输入的密码不一致"
    )

    # 检查账号是否已存在
    query = select(func.count(User.id)).where(
        and_(User.user_account == request.user_account, User.is_delete == 0)
    )
    count = await self.db.fetch_val(query)
    throw_if(count > 0, ErrorCode.USER_ALREADY_EXIST, "账号已存在")

    # 加密密码
    encrypted_password = encrypt_password(request.user_password)


    query = """
        INSERT INTO user (userAccount, userPassword, userName, userRole)
        VALUES (:userAccount, :userPassword, :userName, :userRole)
    """
    user_id = await self.db.execute(
        query=query,
        values={
            "userAccount": request.user_account,
            "userPassword": encrypted_password,
            "userName": f"用户{request.user_account}",
            "userRole": "user"
        }
    )

    return user_id


async def login(self, request: UserLoginRequest) -> LoginUserVO:
    """用户登录"""
    # 校验参数
    throw_if(
        len(request.user_account) < 4,
        ErrorCode.PARAMS_ERROR,
        "账号长度不能小于 4 位"
    )
    throw_if(
        len(request.user_password) < 8,
        ErrorCode.PARAMS_ERROR,
        "密码长度不能小于 8 位"
    )

    # 查询用户
    query = select(User).where(
        and_(User.user_account == request.user_account, User.is_delete == 0)
    )
    user = await self.db.fetch_one(query)
    throw_if_not(user, ErrorCode.USER_NOT_EXIST, "用户不存在")

    # 验证密码
    encrypted_password = encrypt_password(request.user_password)
    throw_if(
        user["userPassword"] != encrypted_password,
        ErrorCode.PASSWORD_ERROR,
        "密码错误"
    )

    # 返回登录用户信息
    return LoginUserVO(
        id=user["id"],
        userAccount=user["userAccount"],
        userName=user["userName"],
        userAvatar=user["userAvatar"],
        userProfile=user["userProfile"],
        userRole=user["userRole"],
        createTime=user["createTime"].isoformat(),
        updateTime=user["updateTime"].isoformat()
    )
