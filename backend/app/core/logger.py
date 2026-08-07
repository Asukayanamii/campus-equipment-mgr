# core/logger.py
import logging

# 全局日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 导出全局logger，其他文件直接导入
logger = logging.getLogger(__name__)