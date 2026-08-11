from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.core.exceptions import BussinessException


def _get_fast_mail() -> FastMail:
    """根据配置创建邮件客户端，避免将发件人信息写死在业务代码中。"""
    required_settings = (
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD,
        settings.MAIL_FROM,
        settings.MAIL_SERVER,
    )
    if not all(required_settings):
        raise BussinessException("邮箱服务配置不完整", status_code=500)

    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(mail_config)


async def send_email_verification_code(email: str, verification_code: str) -> None:
    """向指定邮箱发送 60 秒有效的登录验证码。"""
    message = MessageSchema(
        subject="校园设备管理系统邮箱验证码",
        recipients=[email],
        body=(
            f"您的邮箱验证码为：<b>{verification_code}</b>，"
            "有效期为 60 秒，请勿向他人泄露。"
        ),
        subtype=MessageType.html,
    )
    await _get_fast_mail().send_message(message)
