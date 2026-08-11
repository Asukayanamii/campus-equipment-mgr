import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 当前文件：backend/app/core/config.py
current_file_dir = os.path.dirname(__file__)
# 向上两级：backend/
backend_root = os.path.join(current_file_dir, "..", "..")
# 拼接 backend/.env 绝对路径
env_file_abs = os.path.join(backend_root, ".env")

class Settings(BaseSettings):
    # Redis 缓存配置；Redis 不可用时查询接口自动回源 MySQL。
    REDIS_HOST: str = Field("127.0.0.1", description="Redis 主机地址")
    REDIS_PORT: int = Field(6379, description="Redis 端口")
    REDIS_DB: int = Field(0, description="Redis 数据库编号")
    REDIS_PASSWORD: str | None = Field(None, description="Redis 密码")
    REDIS_SOCKET_TIMEOUT: float = Field(0.5, description="Redis 请求超时时间，单位秒")
    EQUIPMENT_QUERY_CACHE_TTL: int = Field(300, ge=1, description="设备查询缓存有效期，单位秒")

    #数据库配置
    DB_HOST: str = Field(..., description="数据库主机地址")
    DB_PORT: int = Field(..., description="数据库端口")
    DB_USER: str = Field(..., description="数据库用户名")
    DB_PASSWORD: str = Field(..., description="数据库密码")
    DB_DATABASE: str = Field(..., description="数据库名称")

    DB_POOL_SIZE: int = Field(10, description="数据库连接池大小")
    DB_MAX_OVERFLOW: int = Field(20, description="数据库连接池最大溢出连接数")

    #JWT配置
    USER_JWT_SECRET_KEY: str = Field(..., description="学生端 JWT 密钥")
    ADMIN_JWT_SECRET_KEY: str = Field(..., description="管理员端 JWT 密钥")
    REPAIR_JWT_SECRET_KEY: str = Field(..., description="维修端 JWT 密钥")
    ALGORITHM: str = Field("HS256", description="JWT 签名算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 12, description="访问令牌有效期，单位为分钟")

    #oss配置
    ALIYUN_OSS_ACCESS_KEY_ID: str = Field(..., description="阿里云 OSS AccessKey ID")
    ALIYUN_OSS_ACCESS_KEY_SECRET: str = Field(..., description="阿里云 OSS AccessKey Secret")
    ALIYUN_OSS_REGION: str = Field(..., description="阿里云 OSS 区域")
    ALIYUN_OSS_BUCKET_NAME: str = Field(..., description="阿里云 OSS 存储桶名称")

    #图片上传配置
    IMAGE_MAX_SIZE: int = Field(..., description="图片上传大小上限")
    IMAGE_ALLOWED_EXTENSIONS: str = Field(..., description="允许上传的图片扩展名")
    IMAGE_ALLOWED_CONTENT_TYPES: str = Field(
        "image/jpeg,image/png,image/gif,image/webp",
        description="允许上传的图片 MIME 类型",
    )
    DEFAULT_EQUIPMENT_IMAGE_URL: str = Field(..., description="新增设备的默认图片 URL")
    DEFAULT_PROFILE_IMAGE_URL: str = Field(..., description="新账号的默认头像 URL")

    SUPER_ADMIN_USERNAME: str = Field(..., description="super administrator username")

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @property
    def JWT_SECRET_KEY_ALGORITHM(self) -> tuple[str,str]:
        return self.JWT_SECRET_KEY, self.ALGORITHM

    model_config = SettingsConfigDict(
        env_file=env_file_abs,
        env_file_encoding="utf-8"
    )

settings = Settings()
