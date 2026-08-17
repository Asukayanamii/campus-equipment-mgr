import alibabacloud_oss_v2 as oss

from app.core.config import settings
from app.core.exceptions import BussinessException
from app.core.logger import logger


#oss上传文件
def upload(file: bytes, object_name: str):

    region = settings.ALIYUN_OSS_REGION
    bucket_name = settings.ALIYUN_OSS_BUCKET_NAME

    # Loading credentials values from the environment variables
    credentials_provider = oss.credentials.StaticCredentialsProvider(
        access_key_id=settings.ALIYUN_OSS_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_OSS_ACCESS_KEY_SECRET,
    )

    # Using the SDK's default configuration
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = region

    client = oss.Client(cfg)

    result = client.put_object(oss.PutObjectRequest(
        bucket=bucket_name,
        key=object_name,
        body=file,
    ))

    logger.info(f'put object successfully, ETag {result.etag}')

    file_url = f"https://{bucket_name}."+"oss-"+f"{region}.aliyuncs.com"+f"/{object_name}"

    return file_url

def upload_image(file: bytes, object_name: str, content_type: str | None = None):
    """校验图片类型和大小后上传 OSS，供所有图片业务统一使用。"""
    allow_ext = {
        extension.strip().lower().lstrip(".")
        for extension in settings.IMAGE_ALLOWED_EXTENSIONS.split(",")
        if extension.strip()
    }
    allow_content_types = {
        value.strip().lower()
        for value in settings.IMAGE_ALLOWED_CONTENT_TYPES.split(",")
        if value.strip()
    }

    ext = object_name.split(".")[-1].lower()

    if ext not in allow_ext:
        logger.error("文件格式错误")
        raise BussinessException("图片格式不支持")
    if content_type and content_type.lower() not in allow_content_types:
        logger.error("文件 MIME 类型错误")
        raise BussinessException("图片 MIME 类型不支持")
    if len(file) > settings.IMAGE_MAX_SIZE * 1024 * 1024:
        logger.error("文件过大")
        raise BussinessException(f"文件必须小于{settings.IMAGE_MAX_SIZE}MB")
    object_name = "images/"+object_name
    try:
        s = upload(file, object_name)
    except Exception as e:
        logger.error(e)
        raise BussinessException("上传失败")
    return s


def upload_evidence_image(file: bytes, object_name: str, content_type: str | None = None):
    """上传归还损坏或维修凭证图片，复用统一图片上传和校验逻辑。"""
    return upload_image(file, object_name, content_type)
