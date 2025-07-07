#!/usr/bin/env python3
"""
MCP智能路由系统启动脚本
提供便捷的系统启动方式
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.client.mcp_client_pro import main
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_environment():
    """检查环境配置"""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  未找到 .env 配置文件")
        print("请将 .env.example 复制为 .env 并填入正确的配置信息")
        return False
    
    # 检查基本配置
    from config.settings import settings
    try:
        if not settings.validate():
            print("❌ 配置验证失败，请检查 .env 文件中的配置")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    return True


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    MCP智能路由系统                           ║
║                 Intelligent AI Router                       ║
║                                                              ║
║  🤖 支持数学推理、视觉理解、文本处理等多种AI任务               ║
║  🚀 基于MCP协议的智能模型路由                                 ║
║  ⚡ 高性能、高可靠性的AI助手系统                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main_entry():
    """主入口函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    print("✅ 环境检查通过")
    print("🚀 正在启动MCP智能路由系统...")
    print()
    
    try:
        # 启动主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用MCP智能路由系统！")
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_entry()