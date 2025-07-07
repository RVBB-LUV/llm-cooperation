"""
MCP服务器主模块
提供统一的MCP工具接口，支持多种AI模型的智能路由
"""
import sys
import os
import asyncio
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from mcp.server.fastmcp import FastMCP
from config.settings import settings
from src.common.logger import get_logger
from src.common.exceptions import MCPServerError, ValidationError
from src.common.utils import format_error_message
from src.server.ai_models import ai_model_manager

# 初始化日志和配置
logger = get_logger(__name__)

# 验证配置
if not settings.validate():
    logger.error("Configuration validation failed")
    sys.exit(1)

# 初始化MCP服务器
mcp = FastMCP("intelligent_ai_router")
logger.info("MCP Server initialized successfully")


@mcp.tool()
async def math_code(query: str) -> str:
    """
    数学和编程推理工具
    
    使用高性能推理模型处理复杂的数学证明、代码调试和策略分析任务。
    适用于需要深度逻辑推理的复杂问题。
    
    Args:
        query (str): 需要处理的数学或编程问题
        
    Returns:
        str: 详细的推理过程和解决方案
        
    Examples:
        - 数学证明：证明费马大定理的特殊情况
        - 代码调试：分析并修复递归算法中的逻辑错误
        - 策略分析：评估不同算法的时间复杂度和空间复杂度
    """
    try:
        logger.info(f"Processing math_code request: {query[:100]}...")
        
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
        
        # 调用AI模型管理器
        result = await ai_model_manager.math_code_inference(query)
        
        logger.info("Math_code processing completed successfully")
        return result
        
    except Exception as e:
        error_msg = format_error_message(e, "math_code tool")
        logger.error(error_msg)
        return f"处理失败：{error_msg}"


@mcp.tool()
async def VL_mode(query: str) -> str:
    """
    视觉理解和多模态推理工具
    
    使用多模态模型处理图像理解、跨模态推理和视觉问答任务。
    能够分析图像内容并结合文本进行综合推理。
    能够根据用户给出的图片链接读取图片内容。
    
    Args:
        query (str): 包含视觉任务描述的查询内容，其中可能包含URL
        
    Returns:
        str: 视觉分析结果和推理结论
        
    Examples:
        - 图像描述：详细描述图片中的对象、场景和关系
        - 视觉问答：基于图像内容回答相关问题
        - 跨模态推理：结合图像和文本信息进行综合分析
    """
    try:
        logger.info(f"Processing VL_mode request: {query[:100]}...")
        print("11111111111111111111111111111111")
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
        
        # 尝试从query中提取URL
        import re
        url_match = re.search(r'(https?://\S+)', query)
        extracted_url = url_match.group(1) if url_match else None

        if not extracted_url:
            raise ValidationError("No URL found in the query for VL_mode.")

        # 移除query中的URL，只保留文本部分
        cleaned_query = re.sub(r'(https?://\S+)', '', query).strip()
        # print("11111111111111111111111111111111")
        # 调用AI模型管理器
        result = await ai_model_manager.vision_processing(cleaned_query, extracted_url)
        
        logger.info("VL_mode processing completed successfully")
        return result
        
    except Exception as e:
        error_msg = format_error_message(e, "VL_mode tool")
        logger.error(error_msg)
        return f"处理失败：{error_msg}"


@mcp.tool()
async def light_mode(query: str) -> str:
    """
    轻量级文本处理工具
    
    使用高效模型处理简单的文本任务，如文本润色、基础翻译、信息提取等。
    响应速度快，适合对延迟敏感的基础文本处理需求。
    
    Args:
        query (str): 需要处理的文本内容
        
    Returns:
        str: 处理后的文本结果
        
    Examples:
        - 文本润色：改善文章的语言表达和流畅度
        - 基础翻译：中英文等常见语言间的翻译
        - 信息提取：从文本中提取关键信息和实体
        - 格式转换：不同文本格式间的标准化转换
    """
    try:
        logger.info(f"Processing light_mode request: {query[:100]}...")
        
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
        
        # 调用AI模型管理器
        result = await ai_model_manager.light_processing(query)
        
        logger.info("Light_mode processing completed successfully")
        return result
        
    except Exception as e:
        error_msg = format_error_message(e, "light_mode tool")
        logger.error(error_msg)
        return f"处理失败：{error_msg}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    数学加法工具（示例工具）
    
    执行两个整数的加法运算。这是一个简单的示例工具，
    展示了MCP工具的基本结构和参数处理方式。
    
    Args:
        a (int): 第一个加数
        b (int): 第二个加数
        
    Returns:
        int: 两数之和
        
    Examples:
        add(3, 5) -> 8
        add(-2, 7) -> 5
    """
    try:
        logger.info(f"Performing addition: {a} + {b}")
        
        if not isinstance(a, int) or not isinstance(b, int):
            raise ValidationError("Both parameters must be integers")
        
        result = a + b
        logger.info(f"Addition result: {result}")
        return result
        
    except Exception as e:
        error_msg = format_error_message(e, "add tool")
        logger.error(error_msg)
        raise MCPServerError(error_msg)


def main():
    """
    启动MCP服务器
    
    服务器启动后会监听客户端连接，并处理工具调用请求。
    支持的工具包括数学推理、视觉理解、轻量级文本处理等。
    """
    try:
        logger.info("Starting MCP Server...")
        logger.info(f"Available tools: math_code, VL_mode, light_mode, add")
        logger.info(f"Using models - Math: {settings.model.math_model}, "
                   f"Vision: {settings.model.vision_model}, "
                   f"Light: {settings.model.light_model}")
        
        # 启动服务器
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        error_msg = format_error_message(e, "MCP Server startup")
        logger.error(error_msg)
        raise MCPServerError(error_msg)
    finally:
        logger.info("MCP Server shutdown completed")


if __name__ == "__main__":
    main()