class BussinessException(Exception):
    """
    业务异常
    """
    def __init__(self, message: str, status_code: int = 400):
        self.status_code = status_code
        self.message = message
    def __str__(self):
        return f"{self.status_code} - {self.message}"