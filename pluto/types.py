"""
Pluto 数据引擎的类型定义
"""

from enum import Enum

class APIProvider(Enum):
    """枚举定义支持的 API 提供商类型"""
    DEFAULT = "default"  # 默认 OpenAI/Azure 等
    OLLAMA = "ollama"    # Ollama 本地模型
    OPENAI_COMPATIBLE = "openai_compatible"  # 自定义 base URL 的 OpenAI 兼容接口
    OPENROUTER = "openrouter"  # OpenRouter 接口