"""自定义业务异常类"""


class BaseAPIException(Exception):
    """基础 API 异常类，支持日志记录"""
    def __init__(self, message, details=None, level='error'):
        self.message = message
        self.details = details or {}
        self.level = level
        super().__init__(message)


class PaymentException(BaseAPIException):
    """支付相关异常"""
    pass


class CodeExecutionException(BaseAPIException):
    """代码执行异常"""
    pass


class FileOperationException(BaseAPIException):
    """文件操作异常"""
    pass


class CourseEnrollmentException(BaseAPIException):
    """课程注册异常"""
    pass


class AuthenticationException(BaseAPIException):
    """认证相关异常"""
    pass


class ValidationException(BaseAPIException):
    """数据验证异常"""
    pass