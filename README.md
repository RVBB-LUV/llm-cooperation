
# MCP智能路由系统

一个基于Model Context Protocol (MCP)的智能AI模型路由系统，能够根据任务特性自动选择最适合的AI模型进行处理。

## 🌟 主要特性

- **智能路由**: 根据任务类型自动选择最适合的AI模型
- **多模态支持**: 支持文本、数学推理、视觉理解等多种任务类型
- **高可靠性**: 完善的错误处理和重试机制
- **可扩展性**: 基于MCP协议，易于添加新的AI工具
- **配置化**: 支持灵活的配置管理
- **详细日志**: 完整的操作日志记录

## 🏗️ 项目结构

```
MCP代码/
├── src/
│   ├── server/           # MCP服务器模块
│   │   ├── mcp_server.py # 主服务器文件
│   │   └── ai_models.py  # AI模型管理器
│   ├── client/           # MCP客户端模块
│   │   └── mcp_client.py # 主客户端文件
│   └── common/           # 通用模块
│       ├── logger.py     # 日志管理
│       ├── exceptions.py # 异常定义
│       ├── utils.py      # 工具函数
│       └── prompts.py    # 提示词管理
├── config/
│   └── settings.py       # 配置管理
├── logs/                 # 日志文件目录
├── tests/                # 测试文件目录
├── .env                  # 环境变量文件
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

确保已安装Python 3.8+和所需依赖：

```bash
pip install mcp openai python-dotenv
```

### 2. 配置环境变量

创建`.env`文件：

```env
# API配置
BASE_URL=https://api2.aigcbest.top/v1
API_KEY=your_api_key_here
MODEL=gpt-4o

# 模型配置
MATH_MODEL=gpt-4o
VISION_MODEL=qwen2.5vl:7b
LIGHT_MODEL=deepseek-r1:7b

# 其他配置
LOG_LEVEL=INFO
API_TIMEOUT=30
MAX_TOKENS=4000
TEMPERATURE=0.7
```

### 3. 启动系统

```bash
# 启动客户端（会自动启动服务器）
python src/client/mcp_client.py
```

## 🎯 支持的任务类型

### 数学和编程推理 (math_code)
- 数学证明和复杂计算
- 代码调试和算法优化
- 逻辑推理和策略分析
- 复杂问题的深度思考

**示例使用场景**:
- "证明勾股定理"
- "优化这个排序算法的时间复杂度"
- "分析这段代码的逻辑错误"

### 视觉理解 (VL_mode)
- 图像分析和描述
- 图文混合内容处理
- 视觉问答
- 跨模态推理

**示例使用场景**:
- "分析这张图片中的内容"
- "根据图片回答相关问题"
- "描述图片中的场景和对象"

### 轻量级处理 (light_mode)
- 文本润色和编辑
- 基础翻译和转换
- 信息提取和摘要
- 快速文本处理

**示例使用场景**:
- "润色这段文字"
- "将这段中文翻译成英文"
- "提取文本中的关键信息"

## 📝 使用示例

### 交互式使用

启动程序后，可以直接输入查询：

```
🤖 请输入您的问题: 请帮我证明费马小定理

🔄 正在处理您的请求...

============================================================
📋 处理结果:
------------------------------------------------------------
费马小定理证明：

如果p是质数，a是不被p整除的整数，则：
a^(p-1) ≡ 1 (mod p)

证明过程：
1. 考虑集合 S = {1, 2, 3, ..., p-1}
2. 对于不被p整除的整数a，集合 T = {a·1, a·2, a·3, ..., a·(p-1)} 
3. 由于gcd(a,p) = 1，所以T中的元素模p后仍为{1, 2, 3, ..., p-1}的一个排列
...
============================================================
```

### 编程接口使用

```python
import asyncio
from src.client.mcp_client import MCPClient

async def example():
    client = MCPClient()
    await client.connect_to_server('./src/server/mcp_server.py')
    
    # 处理数学问题
    result = await client.process_query("计算fibonacci数列的第10项")
    print(result)
    
    await client.cleanup()

asyncio.run(example())
```

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BASE_URL` | API基础URL | https://api2.aigcbest.top/v1 |
| `API_KEY` | API密钥 | 必填 |
| `MODEL` | 默认模型 | gpt-4o |
| `MATH_MODEL` | 数学推理模型 | gpt-4o |
| `VISION_MODEL` | 视觉理解模型 | qwen2.5vl:7b |
| `LIGHT_MODEL` | 轻量级模型 | deepseek-r1:7b |
| `LOG_LEVEL` | 日志级别 | INFO |
| `API_TIMEOUT` | API超时时间(秒) | 30 |
| `MAX_TOKENS` | 最大token数 | 4000 |
| `TEMPERATURE` | 模型温度参数 | 0.7 |

### 日志配置

日志文件位于`logs/mcp_system.log`，支持自动轮转：
- 最大文件大小：10MB
- 保留备份数：5个
- 支持控制台和文件双重输出

## 🛠️ 开发指南

### 添加新的AI工具

1. 在`src/server/ai_models.py`中添加新的模型处理方法
2. 在`src/server/mcp_server.py`中注册新的MCP工具
3. 更新提示词管理器以支持新工具

### 自定义提示词

编辑`src/common/prompts.py`中的提示词模板：

```python
def _get_custom_prompt(self) -> str:
    return """你的自定义提示词内容"""
```

### 错误处理

系统提供了完善的异常处理机制：

```python
from src.common.exceptions import MCPClientError, APIError

try:
    result = await client.process_query("your query")
except MCPClientError as e:
    print(f"客户端错误: {e}")
except APIError as e:
    print(f"API错误: {e}")
```

## 📊 性能优化

### 重试机制
- 自动重试失败的API调用
- 指数退避算法
- 可配置的重试次数和间隔

### 超时控制
- API调用超时保护
- 可配置的超时时间
- 优雅的超时处理

### 资源管理
- 异步上下文管理器
- 自动资源清理
- 内存泄漏防护

## 🔧 故障排除

### 常见问题

1. **连接服务器失败**
   - 检查服务器脚本路径是否正确
   - 确认Python环境和依赖是否完整

2. **API调用失败**
   - 验证API密钥是否正确
   - 检查网络连接状态
   - 确认API配额是否充足

3. **工具调用错误**
   - 查看日志文件获取详细错误信息
   - 验证输入参数格式是否正确

### 日志分析

查看`logs/mcp_system.log`文件了解详细的运行状态：

```bash
tail -f logs/mcp_system.log
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 🙏 致谢

- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - 核心协议支持
- [OpenAI](https://openai.com/) - API服务
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP服务器框架