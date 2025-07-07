"""
自定义异常类
定义项目中使用的各种异常类型
"""


class MCPError(Exception):
    """MCP相关异常的基类"""
    pass


class MCPServerError(MCPError):
    """MCP服务器异常"""
    pass


class MCPClientError(MCPError):
    """MCP客户端异常"""
    pass


class APIError(MCPError):
    """API调用异常"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ModelError(MCPError):
    """模型相关异常"""
    pass


class ConfigurationError(MCPError):
    """配置相关异常"""
    pass


class ValidationError(MCPError):
    """数据验证异常"""
    pass


class TimeoutError(MCPError):
    """超时异常"""
    pass


class RetryExhaustedError(MCPError):
    """重试次数耗尽异常"""
    pass