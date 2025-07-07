"""
MCP客户端主模块 - 优化版
负责与MCP服务器通信，处理用户查询和工具调用
"""
import sys
import os
import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from pathlib import Path
from urllib.parse import quote_plus

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.settings import settings
from src.common.logger import get_logger
from src.common.exceptions import MCPClientError, APIError, ValidationError
from src.common.utils import (
    validate_json, 
    validate_tool_call, 
    sanitize_input,
    retry_with_backoff,
    timeout_wrapper,
    format_error_message
)
from src.common.prompts import prompt_manager, PromptType

logger = get_logger(__name__)


class MCPClient:
    """MCP客户端类 - 优化版"""
    
    def __init__(self):
        """初始化MCP客户端"""
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None
        self.stdio = None
        self.write = None
        
        # 初始化OpenAI客户端
        self.ai_client = AsyncOpenAI(
            base_url=settings.api.base_url,
            api_key=settings.api.api_key,
        )
        
        # 连接状态
        self.is_connected = False
        logger.info("MCP Client initialized successfully")
    
    async def connect_to_server(self, server_script_path: str) -> None:
        """连接到MCP服务器"""
        try:
            logger.info(f"Connecting to MCP server: {server_script_path}")
            
            # 验证服务器脚本是否存在
            if not Path(server_script_path).exists():
                raise MCPClientError(f"Server script not found: {server_script_path}")
            
            # 设置服务器参数
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env={"PYTHONUTF8": "1"}
            )
            
            # 建立stdio连接
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            
            # 创建客户端会话
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            
            # 初始化会话
            await self.session.initialize()
            self.is_connected = True
            logger.info("Successfully connected to server")
            
        except Exception as e:
            error_msg = format_error_message(e, "MCP server connection")
            logger.error(error_msg)
            raise MCPClientError(error_msg) from e

    def _validate_connection(self) -> None:
        """验证连接状态"""
        if not self.is_connected or not self.session:
            raise MCPClientError("Not connected to MCP server. Please call connect_to_server() first.")
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    async def _call_ai_model(self, messages: List[Dict[str, str]]) -> str:
        """调用AI模型"""
        try:
            response = await timeout_wrapper(
                self.ai_client.chat.completions.create(
                    model=settings.api.model,
                    messages=messages,
                    max_tokens=settings.model.max_tokens,
                    temperature=settings.model.temperature
                ),
                timeout_seconds=settings.api.timeout
            )
            
            content = response.choices[0].message.content
            print("----------------------------")
            print("content:", content)  # 打印content以检查其内容
            print("----------------------------")
            if not content:
                raise APIError("Empty response from AI model")
            
            return content
            
        except Exception as e:
            error_msg = format_error_message(e, "AI model call")
            logger.error(error_msg)
            raise APIError(error_msg) from e
    
    async def _call_mcp_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """调用MCP工具"""
        try:
            self._validate_connection()
            logger.info(f"Calling MCP tool: {tool_name} with args: {tool_args}")
            # tool_args_json = json.dumps(tool_args)
            result = await self.session.call_tool(tool_name, tool_args)
            
            if not result.content:
                raise MCPClientError(f"Empty result from tool: {tool_name}")
            
            tool_result = result.content[0].text
            logger.info(f"Tool {tool_name} executed successfully")
            return tool_result
            
        except Exception as e:
            error_msg = format_error_message(e, f"MCP tool call: {tool_name}")
            logger.error(error_msg)
            raise MCPClientError(error_msg) from e
    
    async def _get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        try:
            self._validate_connection()
            response = await self.session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in response.tools
            ]
            logger.info(f"Available tools: {[t['function']['name'] for t in tools]}")
            return tools
        except Exception as e:
            error_msg = format_error_message(e, "get available tools")
            logger.error(error_msg)
            raise MCPClientError(error_msg) from e
    
    def _extract_json_from_text(self, text: str) -> tuple:
        """从文本中提取JSON内容"""
        if '```json' not in text:
            return False, text
        # 提取JSON块并去除前后空白字符
        json_block = text.split('```json')[1].split('```')[0].strip()
        return True, json_block
    
    async def process_query(self, query: str) -> str:
        """处理用户查询 - 优化版"""
        try:
            # 验证连接和输入
            self._validate_connection()
            query = sanitize_input(query)
            
            if not query:
                raise ValidationError("Query cannot be empty")
            
            logger.info(f"Processing query: {query[:100]}...")
            
            # 获取工具列表
            available_tools = await self._get_available_tools()
            
            # 构建系统提示词
            system_prompt = prompt_manager.get_prompt(
                PromptType.SYSTEM_ROUTER,
                tools=str(available_tools)
            )
            
            # 构建初始消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # 获取AI模型初始响应
            ai_response = await self._call_ai_model(messages)
            logger.info(f"Initial AI response: {ai_response[:200]}...")
            
            # 工具调用结果收集
            tool_results = []
            max_iterations = 5
            current_iteration = 0
            
            while current_iteration < max_iterations:
                current_iteration += 1
                logger.info(f"Processing iteration {current_iteration}")
                
                # 尝试提取JSON内容
                is_json, content = self._extract_json_from_text(ai_response)
                
                if not is_json:
                    messages= [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query+"，请按照以下格式输出：\n\n```json\n{\"name\": \"工具名称\", \"params\": {\"参数名\": \"参数值\"}}\n```\n\n确保输出的是有效的JSON格式。"}
                    ]
                    ai_response = await self._call_ai_model(messages)
                    logger.info("No tool call detected, re-prompting AI for JSON output.")
                    continue # Continue the loop to re-evaluate the new ai_response
                
                # 解析和验证工具调用
                tool_data = json.loads(content)
                
                # 执行工具调用
                tool_name = tool_data['name']
                tool_args = tool_data['params']

                # 特殊处理VL_mode工具，将url合并到query中
                if tool_name == "VL_mode" and "url" in tool_args:
                    original_query = tool_args.get("query", "")
                    image_url = tool_args.pop("url") # 移除url键
                    tool_args["query"] = f"{original_query} {image_url}"
                
                try:
                    tool_result = await self._call_mcp_tool(tool_name, tool_args)
                    tool_results.append(tool_result)
                    
                    # 更新消息历史
                    messages.append({"role": "assistant", "content": ai_response})
                    messages.append({"role": "user", "content": f"工具调用结果：{tool_result}"})
                    
                    # 添加下一步操作提示
                    next_step_prompt = prompt_manager.get_prompt(PromptType.NEXT_STEP, query=query)
                    messages.append({"role": "user", "content": next_step_prompt})
                    
                    # 获取下一步决策
                    ai_response = await self._call_ai_model(messages)
                    logger.info(f"Next step response: {ai_response}")
                    
                    # 检查是否完成
                    if '<finish>' in ai_response.lower():
                        logger.info("Task completion detected")
                        break
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    # 添加错误信息到消息历史
                    error_msg = f"工具调用失败: {format_error_message(e, tool_name)}"
                    messages.append({"role": "user", "content": error_msg})
                    # 继续处理但跳过当前工具
                    ai_response = await self._call_ai_model(messages)
            
            # 生成最终结果
            if tool_results:
                final_prompt = prompt_manager.get_prompt(
                    PromptType.FINISH_GENERATE,
                    collected_info='\n\n'.join(tool_results),
                    query=query
                )
                messages.append({"role": "user", "content": final_prompt})
                final_response = await self._call_ai_model(messages)
                logger.info("Query processing completed successfully")
                return final_response
            else:
                logger.warning("No tool results collected")
                return "处理完成，但未获取到有效结果。"
            
        except Exception as e:
            error_msg = format_error_message(e, "query processing")
            logger.error(error_msg)
            raise MCPClientError(error_msg) from e
    
    async def chat_loop(self) -> None:
        """启动交互式聊天循环 - 优化版"""
        print("\nMCP智能路由助手已启动!")
        print("输入您的问题或需求，输入 'quit' 退出程序")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n🤖 请输入您的问题: ").strip()
                
                if query.lower() in ['quit', 'exit', '退出', 'q']:
                    print("感谢使用！再见！")
                    break
                
                if not query:
                    print("请输入有效的问题")
                    continue
                
                print("\n🔄 正在处理您的请求...")
                response = await self.process_query(query)
                
                print("\n" + "="*60)
                print("📋 处理结果:")
                print("-" * 60)
                print(response)
                print("="*60)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断，正在退出...")
                break
            except Exception as e:
                error_msg = format_error_message(e, "chat loop")
                logger.error(error_msg)
                print(f"\n❌ 发生错误: {error_msg}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
            self.is_connected = False
            logger.info("MCP Client cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def main():
    """主函数 - 优化版"""
    client = None
    try:
        client = MCPClient()
        server_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'server', 'mcp_server.py')
        await client.connect_to_server(server_path)
        await client.chat_loop()
    except Exception as e:
        error_msg = format_error_message(e, "main")
        logger.error(error_msg)
        print(f"启动失败: {error_msg}")
    finally:
        if client:
            await client.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常退出: {e}")