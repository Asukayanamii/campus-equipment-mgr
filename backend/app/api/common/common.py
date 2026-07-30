import uuid
from fastapi import APIRouter, File, Depends, UploadFile

from app.core.auth import varity_from_three_client
from app.core.logger import logger
from app.result.result import Result
from app.utils import oss_util

router = APIRouter(prefix="/common", tags=["通用接口"])

@router.post("/upload-image", name="上传图片文件",response_model=Result[str],dependencies=[Depends(varity_from_three_client)])
def upload_image(file: UploadFile = File(...)):
    logger.info("上传图片文件")
    file_name = file.filename
    ext = file_name.split(".")[-1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return Result.success(oss_util.upload_image(file.file.read(), new_filename))