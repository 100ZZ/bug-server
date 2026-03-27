#!/usr/bin/env python3
"""启动服务器脚本，配置日志过滤器"""
import logging
import sys
from logging import Filter

class Filter401(Filter):
    """过滤 401 未授权访问日志"""
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        # 过滤包含 401 Unauthorized 的日志
        if ' 401 ' in msg or '401 Unauthorized' in msg:
            return False
        # 检查 status_code 属性
        if hasattr(record, 'status_code') and record.status_code == 401:
            return False
        return True

# 配置 uvicorn 访问日志过滤器（在启动前配置）
access_logger = logging.getLogger('uvicorn.access')
if not any(isinstance(f, Filter401) for f in access_logger.filters):
    access_logger.addFilter(Filter401())

# 同时也配置默认的 logger，因为某些情况下日志可能走默认 logger
default_logger = logging.getLogger()
for handler in default_logger.handlers:
    if not any(isinstance(f, Filter401) for f in handler.filters):
        handler.addFilter(Filter401())

# 导入并运行 uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # 配置日志格式，但不禁用访问日志（因为我们用过滤器来过滤）
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=43211,
        # 使用自定义日志配置来确保过滤器生效
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "filter_401": {
                    "()": Filter401,
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "stream": "ext://sys.stdout",
                    "filters": ["filter_401"],
                },
                "access": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "stream": "ext://sys.stdout",
                    "filters": ["filter_401"],
                },
            },
            "loggers": {
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["access"],
                    "propagate": False,
                },
            },
            # 让应用内 logger.info()（如 app 模块）输出到控制台
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )
