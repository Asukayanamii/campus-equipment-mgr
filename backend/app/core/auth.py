import jwt
from fastapi import Depends, Header

from app.core.config import settings
from app.core.exceptions import BussinessException

#三端鉴权依赖函数
def user_verity(token: str | None = Header(None)):
    if not token:
        raise BussinessException("未登录，请先登录", status_code=401)
    try:
        info = jwt.decode(token, settings.USER_JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise BussinessException("登录已过期或未登录，请重新登录", status_code=401)
    return info

def admin_verity(token: str | None = Header(None)):
    if not token:
        raise BussinessException("未登录，请先登录", status_code=401)
    try:
        info = jwt.decode(token, settings.ADMIN_JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise BussinessException("登录已过期或未登录，请重新登录", status_code=401)
    return info

def repair_verity(token: str | None = Header(None)):
    if not token:
        raise BussinessException("未登录，请先登录", status_code=401)
    try:
        info = jwt.decode(token, settings.REPAIR_JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise BussinessException("登录已过期或未登录，请重新登录", status_code=401)
    return info

def varity_from_three_client(token: str | None = Header(None)) -> dict | None:
    """
    三端选鉴权,判断是否登录其一
    """
    flag = False
    try:
        info = user_verity( token)
        flag = True
    except BussinessException:
        try:
            info = admin_verity( token)
            flag = True
        except BussinessException:
            try:
                info = repair_verity( token)
                flag = True
            except BussinessException:
                flag = False
    if not flag:
        raise BussinessException("未登录，请先登录", status_code=401)
    return info
