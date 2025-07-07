"""
AI模型管理模块
统一管理所有AI模型的调用接口
"""
import sys
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

# 添加项目根目录到路径，以便导入config模块
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config.settings import settings
from src.common.logger import get_logger
from src.common.exceptions import APIError, ModelError, ValidationError
from src.common.utils import retry_with_backoff, sanitize_input, format_error_message, timeout_wrapper
from src.common.prompts import prompt_manager, PromptType

logger = get_logger(__name__)


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.client = AsyncOpenAI(
            base_url=settings.api.base_url,
            api_key=settings.api.api_key
        )
        logger.info("AI model manager initialized successfully")
    
    def _validate_query(self, query: str, allow_empty: bool = False) -> str:
        """
        验证和清理查询内容
        
        Args:
            query: 原始查询内容
            allow_empty: 是否允许查询内容为空
            
        Returns:
            str: 清理后的查询内容
            
        Raises:
            ValidationError: 查询内容无效
        """
        if query is None:
            raise ValidationError("Query cannot be None")
        
        if not isinstance(query, str):
            raise ValidationError(f"Query must be string, got {type(query)}")
        
        query = sanitize_input(query)
        if not query and not allow_empty:
            raise ValidationError("Query cannot be empty after sanitization")
        
        return query
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    async def _make_api_call(self, model: str, messages: list, prompt_type: PromptType) -> str:
        """
        执行API调用
        
        Args:
            model: 模型名称
            messages: 消息列表
            prompt_type: 提示词类型
            
        Returns:
            str: API响应内容
            
        Raises:
            APIError: API调用失败
        """
        try:
            logger.info(f"Making API call to model: {model}")
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=settings.model.max_tokens,
                temperature=settings.model.temperature
            )
            
            content = response.choices[0].message.content
            if not content:
                raise APIError("Empty response from API")
            
            logger.info(f"API call successful for {prompt_type.value}")
            return content
            
        except Exception as e:
            error_msg = format_error_message(e, f"API call to {model}")
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
    async def math_code_inference(self, query: str) -> str:
        """
        执行数学和编程推理任务
        
        Args:
            query: 查询内容
            
        Returns:
            str: 推理结果
            
        Raises:
            ModelError: 模型处理失败
        """
        try:
            query = self._validate_query(query)
            
            # 获取专门的数学编程提示词
            system_prompt = prompt_manager.get_prompt(PromptType.MATH_CODE, query=query)
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are a professional mathematics and programming assistant with deep reasoning capabilities."
                },
                {
                    "role": "user", 
                    "content": f"User Query: {query}\n\n{system_prompt}"
                }
            ]
            
            result = await self._make_api_call(
                settings.model.math_model, 
                messages, 
                PromptType.MATH_CODE
            )
            
            return result
            
        except Exception as e:
            error_msg = format_error_message(e, "math_code_inference")
            logger.error(error_msg)
            raise ModelError(error_msg) from e
    
    async def vision_processing(self, query: str, url: str) -> str:
        """
        执行视觉理解任务
        
        Args:
            query: 查询内容（可能包含图像引用）
            url: 图像URL地址
            
        Returns:
            str: 视觉处理结果
            
        Raises:
            ModelError: 模型处理失败
        """
        try:
            query = self._validate_query(query, allow_empty=True)
            
            # 获取视觉任务提示词
            system_prompt = prompt_manager.get_prompt(PromptType.VISION, query=query)
            
            messages = [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ]
            logger.info(f"Vision API messages: {messages}")
            
            result = await self._make_api_call(
                settings.model.vision_model, 
                messages, 
                PromptType.VISION
            )
            
            return result
            
        except Exception as e:
            error_msg = format_error_message(e, "vision_processing")
            logger.error(error_msg)
            raise ModelError(error_msg) from e
    
    async def light_processing(self, query: str) -> str:
        """
        执行轻量级处理任务
        
        Args:
            query: 查询内容
            
        Returns:
            str: 处理结果
            
        Raises:
            ModelError: 模型处理失败
        """
        try:
            query = self._validate_query(query)
            
            # 获取轻量级任务提示词
            system_prompt = prompt_manager.get_prompt(PromptType.LIGHT, query=query)
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are an efficient text processing assistant focused on quick and accurate basic tasks."
                },
                {
                    "role": "user", 
                    "content": f"User Query: {query}\n\n{system_prompt}"
                }
            ]
            
            result = await self._make_api_call(
                settings.model.light_model, 
                messages, 
                PromptType.LIGHT
            )
            
            return result
            
        except Exception as e:
            error_msg = format_error_message(e, "light_processing")
            logger.error(error_msg)
            raise ModelError(error_msg) from e


# 全局模型管理器实例
ai_model_manager = AIModelManager()