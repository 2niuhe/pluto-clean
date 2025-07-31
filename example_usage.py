#!/usr/bin/env python3
"""
数据引擎扩展功能使用示例
演示如何使用不同的 API 提供商：Ollama、OpenAI兼容接口、OpenRouter
"""

from pluto.data_engine import DataEngine, EngineArguments
from pluto.topic_tree import TopicTree, TopicTreeArguments
from pluto.types import APIProvider


def example_ollama_usage():
    """Ollama 使用示例"""
    print("=== Ollama 使用示例 ===")

    # 创建引擎参数
    args = EngineArguments(
        instructions="生成高质量的对话数据", system_prompt="你是一个有用的AI助手。"
    )

    # 创建数据引擎
    engine = DataEngine(args)

    # 使用 Ollama
    try:
        engine.create_data(
            model_name="llama3.1",
            num_steps=2,
            batch_size=5,
            api_provider=APIProvider.OLLAMA,
            api_base="http://localhost:11434",
        )
        print("✓ Ollama 调用成功")
    except Exception as e:
        print(f"✗ Ollama 调用失败: {e}")


def example_openai_compatible_usage():
    """OpenAI 兼容接口使用示例"""
    print("\n=== OpenAI 兼容接口使用示例 ===")

    args = EngineArguments(
        instructions="生成技术文档相关的对话数据", system_prompt="你是一个技术专家。"
    )

    engine = DataEngine(args)

    try:
        engine.create_data(
            model_name="gpt-3.5-turbo",  # 这将被转换为 openai/gpt-3.5-turbo
            num_steps=2,
            batch_size=3,
            api_provider=APIProvider.OPENAI_COMPATIBLE,
            api_base="http://localhost:8000/v1",  # 你的本地 OpenAI 兼容服务
            api_key="your-api-key-here",
        )
        print("✓ OpenAI 兼容接口调用成功")
    except Exception as e:
        print(f"✗ OpenAI 兼容接口调用失败: {e}")


def example_openrouter_usage():
    """OpenRouter 使用示例"""
    print("\n=== OpenRouter 使用示例 ===")

    args = EngineArguments(
        instructions="生成创意写作相关的对话数据",
        system_prompt="你是一个创意写作助手。",
    )

    engine = DataEngine(args)

    # 方式1：通过参数传递 API key
    try:
        engine.create_data(
            model_name="anthropic/claude-3.5-sonnet",  # 这将被转换为 openrouter/anthropic/claude-3.5-sonnet
            num_steps=2,
            batch_size=3,
            api_provider=APIProvider.OPENROUTER,
            api_key="your-openrouter-api-key",
        )
        print("✓ OpenRouter (通过参数) 调用成功")
    except Exception as e:
        print(f"✗ OpenRouter (通过参数) 调用失败: {e}")

    # 方式2：通过环境变量（推荐）
    # 在运行前设置: export OPENROUTER_API_KEY=your-key
    try:
        engine.create_data(
            model_name="anthropic/claude-3.5-sonnet",
            num_steps=2,
            batch_size=3,
            api_provider=APIProvider.OPENROUTER,
            # api_key 会自动从环境变量 OPENROUTER_API_KEY 读取
        )
        print("✓ OpenRouter (环境变量) 调用成功")
    except Exception as e:
        print(f"✗ OpenRouter (环境变量) 调用失败: {e}")


def example_topic_tree_usage():
    """主题树使用示例"""
    print("\n=== 主题树使用不同 API 提供商示例 ===")

    # Ollama 主题树
    try:
        ollama_args = TopicTreeArguments(
            root_prompt="机器学习",
            model_system_prompt="你是一个AI专家",
            tree_degree=3,
            tree_depth=2,
            api_provider=APIProvider.OLLAMA,
            api_base="http://localhost:11434",
        )
        ollama_tree = TopicTree(ollama_args)
        ollama_tree.build_tree("llama3.1")
        print("✓ Ollama 主题树构建成功")
    except Exception as e:
        print(f"✗ Ollama 主题树构建失败: {e}")

    # OpenRouter 主题树
    try:
        openrouter_args = TopicTreeArguments(
            root_prompt="人工智能伦理",
            model_system_prompt="你是一个AI伦理专家",
            tree_degree=3,
            tree_depth=2,
            api_provider=APIProvider.OPENROUTER,
            api_key="your-openrouter-api-key",  # 或通过环境变量
        )
        openrouter_tree = TopicTree(openrouter_args)
        openrouter_tree.build_tree("anthropic/claude-3.5-sonnet")
        print("✓ OpenRouter 主题树构建成功")
    except Exception as e:
        print(f"✗ OpenRouter 主题树构建失败: {e}")


def main():
    print("Pluto 数据引擎 - 多 API 提供商支持演示")
    print("=" * 50)

    example_ollama_usage()
    example_openai_compatible_usage()
    example_openrouter_usage()
    example_topic_tree_usage()

    print("\n" + "=" * 50)
    print("演示完成！")
    print("\n使用说明：")
    print("1. Ollama: 需要设置 api_provider=APIProvider.OLLAMA")
    print("2. OpenAI 兼容: 需要设置 api_base 和 api_key")
    print("3. OpenRouter: 可通过参数或环境变量 OPENROUTER_API_KEY 设置")
    print("4. 所有提供商都支持在 TopicTree 中使用")


if __name__ == "__main__":
    main()
