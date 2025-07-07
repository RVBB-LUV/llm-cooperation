"""
配置管理模块
负责管理项目的所有配置参数，包括API密钥、模型配置、日志配置等
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


@dataclass
class APIConfig:
    """API配置类"""
    base_url: str
    api_key: str
    model: str
    timeout: int = 1200
    max_retries: int = 3


@dataclass
class LogConfig:
    """日志配置类"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/mcp_system.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class ModelConfig:
    """模型配置类"""
    math_model: str = "claude-3-5-sonnet-20240620"
    vision_model: str = "gpt-4o"
    light_model: str = "gpt-4o"
    max_tokens: int = 4000
    temperature: float = 0.4


class Settings:
    """项目配置管理类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            env_file: 环境变量文件路径，默认为项目根目录下的.env文件
        """
        # 确定项目根目录
        self.project_root = Path(__file__).parent.parent
        
        # 加载环境变量
        if env_file is None:
            env_file = self.project_root / ".env"
        
        if Path(env_file).exists():
            load_dotenv(env_file)
        
        # 初始化各模块配置
        self.api = self._load_api_config()
        self.log = self._load_log_config()
        self.model = self._load_model_config()
        
        # 确保日志目录存在
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
    
    def _load_api_config(self) -> APIConfig:
        """加载API配置"""
        base_url = os.getenv("BASE_URL", "https://api2.aigcbest.top/v1")
        # api_key = os.getenv("API_KEY")
        api_key = "sk-BHJwrDHeR1CXL83svRkwZx0Z9OF4K9LsQDrtEQSbQCCOPA7K"

        if not api_key:
            raise ValueError("API_KEY environment variable is required")
        
        return APIConfig(
            base_url=base_url,
            api_key=api_key,
            model=os.getenv("MODEL", "gpt-4o"),
            timeout=int(os.getenv("API_TIMEOUT", "300")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
        )
    
    def _load_log_config(self) -> LogConfig:
        """加载日志配置"""
        return LogConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE", "logs/mcp_system.log"),
            max_bytes=int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
    
    def _load_model_config(self) -> ModelConfig:
        """加载模型配置"""
        return ModelConfig(
            math_model=os.getenv("MATH_MODEL", "claude-3-5-sonnet-20240620"),
            vision_model=os.getenv("VISION_MODEL", "gpt-4o"), # 此处实际使用时改为对应模型
            light_model=os.getenv("LIGHT_MODEL", "gpt-4o"), # 此处实际使用时改为对应模型
            max_tokens=int(os.getenv("MAX_TOKENS", "4000")),
            temperature=float(os.getenv("TEMPERATURE", "0.4"))
        )
    
    def get_log_file_path(self) -> Path:
        """获取日志文件的完整路径"""
        return self.project_root / self.log.file_path
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        try:
            # 验证API配置
            if not self.api.api_key:
                raise ValueError("API key is required")
            
            if not self.api.base_url:
                raise ValueError("Base URL is required")
            
            # 验证模型配置
            if self.model.temperature < 0 or self.model.temperature > 2:
                raise ValueError("Temperature must be between 0 and 2")
            
            if self.model.max_tokens <= 0:
                raise ValueError("Max tokens must be positive")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# 全局配置实例
settings = Settings()