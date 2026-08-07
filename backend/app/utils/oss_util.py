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

def upload_image(file: bytes, object_name: str):
    ALLOW_EXT = settings.IMAGE_ALLOWED_EXTENSIONS.split(',')

    ext = object_name.split(".")[-1].lower()

    if ext not in ALLOW_EXT:
        logger.error("文件格式错误")
        raise BussinessException("只支持 jpg/png/gif 图片")
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
