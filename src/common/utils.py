"""
通用工具函数
包含项目中使用的各种工具函数
"""
import json
import time
import asyncio
from typing import Optional, Tuple, Dict, Any, Callable
from functools import wraps

from .exceptions import ValidationError, TimeoutError, RetryExhaustedError
from .logger import get_logger

logger = get_logger(__name__)


def extract_json_from_text(text: str) -> Tuple[bool, str]:
    """
    从文本中提取JSON内容
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        Tuple[bool, str]: (是否找到JSON, JSON内容或原文本)
    """
    if not text or '```json' not in text:
        return False, text
    
    try:
        json_content = text.split('```json')[1].split('```')[0].strip()
        return True, json_content
    except IndexError:
        logger.warning("Failed to extract JSON from text")
        return False, text


def validate_json(json_str: str) -> Dict[str, Any]:
    """
    验证并解析JSON字符串
    
    Args:
        json_str: JSON字符串
        
    Returns:
        Dict[str, Any]: 解析后的字典
        
    Raises:
        ValidationError: JSON格式错误
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}")


def validate_tool_call(tool_data: Dict[str, Any]) -> bool:
    """
    验证工具调用数据格式
    
    Args:
        tool_data: 工具调用数据
        
    Returns:
        bool: 是否有效
    """
    required_fields = ['name', 'params']
    
    if not isinstance(tool_data, dict):
        return False
    
    for field in required_fields:
        if field not in tool_data:
            return False
    
    if not isinstance(tool_data['name'], str):
        return False
    
    if not isinstance(tool_data['params'], dict):
        return False
    
    return True


def sanitize_input(text: str) -> str:
    """
    清理用户输入
    
    Args:
        text: 原始输入文本
        
    Returns:
        str: 清理后的文本
    """
    if not isinstance(text, str):
        return ""
    
    # 移除前后空白
    text = text.strip()
    
    # 限制长度
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return text


def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    重试装饰器，支持指数退避
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            
            raise RetryExhaustedError(f"Max retries ({max_retries}) exceeded") from last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            
            raise RetryExhaustedError(f"Max retries ({max_retries}) exceeded") from last_exception
        
        # 根据函数是否为协程选择合适的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


async def timeout_wrapper(coro, timeout_seconds=3000):
    """
    为协程添加超时控制
    
    Args:
        coro: 协程对象
        timeout_seconds: 超时时间（秒）
        
    Returns:
        协程结果
        
    Raises:
        TimeoutError: 超时异常
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")


def format_error_message(error: Exception, context: str = "") -> str:
    """
    格式化错误消息
    
    Args:
        error: 异常对象
        context: 错误上下文
        
    Returns:
        str: 格式化的错误消息
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if context:
        return f"[{context}] {error_type}: {error_message}"
    else:
        return f"{error_type}: {error_message}"