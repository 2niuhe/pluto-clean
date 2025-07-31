# Pluto 数据引擎 - API 提供商支持指南

Pluto 数据引擎现在支持多种 API 提供商，包括 Ollama、自定义 OpenAI 兼容接口和 OpenRouter。

## 支持的 API 提供商

### 1. 默认提供商 (DEFAULT)
适用于 OpenAI、Azure OpenAI 等标准提供商。

```python
from pluto.data_engine import DataEngine, EngineArguments, APIProvider

# 使用默认提供商（OpenAI）
engine = DataEngine(args)
dataset = engine.create_data(
    model_name="gpt-4",
    num_steps=5,
    api_provider=APIProvider.DEFAULT
)
```

### 2. Ollama (OLLAMA)
用于本地运行的 Ollama 模型。

```python
dataset = engine.create_data(
    model_name="llama3.1",
    num_steps=5,
    api_provider=APIProvider.OLLAMA,
    api_base="http://localhost:11434"
)
```

### 3. OpenAI 兼容接口 (OPENAI_COMPATIBLE)
用于自定义的 OpenAI 兼容 API 端点。

```python
dataset = engine.create_data(
    model_name="custom-model",
    num_steps=5,
    api_provider=APIProvider.OPENAI_COMPATIBLE,
    api_base="http://your-server.com/v1",
    api_key="your-api-key"
)
```

### 4. OpenRouter (OPENROUTER)
用于 OpenRouter 平台的模型。

```python
# 方法1：通过参数传递 API key
dataset = engine.create_data(
    model_name="anthropic/claude-3.5-sonnet",
    num_steps=5,
    api_provider=APIProvider.OPENROUTER,
    api_key="your-openrouter-key"
)

# 方法2：通过环境变量（推荐）
# 设置环境变量: export OPENROUTER_API_KEY=your-key
dataset = engine.create_data(
    model_name="anthropic/claude-3.5-sonnet",
    num_steps=5,
    api_provider=APIProvider.OPENROUTER
)
```

## TopicTree 支持

TopicTree 类同样支持所有的 API 提供商：

```python
from pluto.topic_tree import TopicTree, TopicTreeArguments

# Ollama 主题树
args = TopicTreeArguments(
    root_prompt="机器学习",
    api_provider=APIProvider.OLLAMA,
    api_base="http://localhost:11434"
)
tree = TopicTree(args)
tree.build_tree("llama3.1")

# OpenRouter 主题树
args = TopicTreeArguments(
    root_prompt="人工智能",
    api_provider=APIProvider.OPENROUTER,
    api_key="your-key"  # 或通过环境变量
)
tree = TopicTree(args)
tree.build_tree("anthropic/claude-3.5-sonnet")
```

## 参数说明

### DataEngine.create_data() 新参数

- `api_provider`: APIProvider 枚举值，指定要使用的 API 提供商
- `api_base`: API 基础 URL（可选，某些提供商需要）
- `api_key`: API 密钥（可选，某些提供商需要）

### TopicTreeArguments 新参数

- `api_provider`: APIProvider 枚举值
- `api_base`: API 基础 URL（可选）
- `api_key`: API 密钥（可选）

## 模型名称转换

不同的 API 提供商会自动为模型名称添加相应的前缀：

- `OLLAMA`: `model_name` → `ollama/model_name`
- `OPENAI_COMPATIBLE`: `model_name` → `openai/model_name`
- `OPENROUTER`: `model_name` → `openrouter/model_name`
- `DEFAULT`: `model_name` 保持不变

## 环境变量

### OpenRouter
设置 `OPENROUTER_API_KEY` 环境变量：
```bash
export OPENROUTER_API_KEY=your-openrouter-api-key
```



## 错误处理

各个提供商有不同的要求：

- **OPENAI_COMPATIBLE**: 必须提供 `api_base` 和 `api_key`
- **OPENROUTER**: 必须提供 `api_key` 或设置 `OPENROUTER_API_KEY` 环境变量
- **OLLAMA**: `api_base` 可选，默认为 `http://localhost:11434`

## 示例代码

完整的使用示例请参见 `example_usage.py` 文件。

## 注意事项

1. **JSON 格式支持**: Ollama 模型可能不支持 `response_format={"type": "json_object"}`，因此对 Ollama 提供商会跳过此参数
2. **API 密钥安全**: 建议通过环境变量而不是硬编码来设置 API 密钥
3. **网络配置**: 确保能够访问相应的 API 端点
4. **模型可用性**: 确认所使用的模型在相应平台上可用
5. **参数必填**: 不同提供商有不同的必填参数要求，请参考错误处理部分