class RegexConstant:
    """正则表达式常量"""
    USERNAME = r'^[\u4e00-\u9fa5a-zA-Z0-9_]{6,24}$'
    NAME = r'^[\u4e00-\u9fa5a-zA-Z0-9_\-]{2,12}$'
    PASSWORD = r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_!@#$%^&*()-=]{6,24}$'
    # 邮箱正则（通用标准邮箱格式）
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'