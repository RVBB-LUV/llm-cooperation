"""
日志管理模块
提供统一的日志记录功能，支持控制台和文件输出
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from config.settings import settings


class Logger:
    """日志管理器"""
    
    _loggers = {}  # 缓存已创建的logger
    
    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        获取或创建logger实例
        
        Args:
            name: logger名称
            log_file: 日志文件路径，如果不指定则使用默认配置
            
        Returns:
            logging.Logger: logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.log.level))
        
        # 防止重复添加handler
        if logger.handlers:
            return logger
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.log.level))
        console_formatter = logging.Formatter(settings.log.format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_file_path = log_file or settings.get_log_file_path()
        try:
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=settings.log.max_bytes,
                backupCount=settings.log.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, settings.log.level))
            file_formatter = logging.Formatter(settings.log.format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to create file handler: {e}")
        
        # 缓存logger
        cls._loggers[name] = logger
        
        return logger


def get_logger(name: str) -> logging.Logger:
    """获取logger的便捷函数"""
    return Logger.get_logger(name)