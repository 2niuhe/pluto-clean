# 🌌 Pluto-Clean: Synthetic Data Generation for LLM Fine-Tuning

> 继承自 [redotvideo/pluto](https://github.com/redotvideo/pluto) 项目

A lightweight library for generating high-quality synthetic datasets for LLM fine-tuning with multi-provider API support.

## Features

- **Multi-Provider Support**: Works with OpenAI, Ollama, OpenRouter, and any OpenAI-compatible API
- **Topic Trees**: Generate diverse data using hierarchical topic structures to avoid repetitiveness  
- **Parallel Processing**: Speed up data generation with concurrent API requests
- **Simple API**: Clean and intuitive interface for quick data generation

## Installation

```bash
pip install pluto-clean
```

## Quick Start

### Basic Usage with OpenAI

```python
from pluto import DataEngine, EngineArguments, APIProvider

# Set your OpenAI API key
export OPENAI_API_KEY=your-key

# Create data engine
args = EngineArguments(
    instructions="Generate coding questions and answers about Python",
    system_prompt="You are a helpful programming tutor."
)

engine = DataEngine(args)

# Generate dataset
dataset = engine.create_data(
    model_name="gpt-4",
    num_steps=10,
    batch_size=5
)

dataset.save("python_qa.jsonl")
```

### Using Topic Trees for Diverse Data

```python
from pluto import TopicTree, TopicTreeArguments, DataEngine, EngineArguments

# Create topic tree
tree_args = TopicTreeArguments(
    root_prompt="Python programming concepts",
    tree_degree=5,  # 5 subtopics per level
    tree_depth=2    # 2 levels deep
)

tree = TopicTree(tree_args)
tree.build_tree("gpt-3.5-turbo")

# Generate data using the topic tree
engine_args = EngineArguments(
    instructions="Generate Python programming questions with code examples",
    system_prompt="You are an expert Python developer and teacher."
)

engine = DataEngine(engine_args)
dataset = engine.create_data(
    model_name="gpt-4",
    num_steps=20,
    batch_size=5,
    topic_tree=tree
)

dataset.save("diverse_python_qa.jsonl")
```

## Multi-Provider Support

### Ollama (Local Models)

```python
from pluto import APIProvider

dataset = engine.create_data(
    model_name="llama3.1",
    num_steps=10,
    api_provider=APIProvider.OLLAMA,
    api_base="http://localhost:11434"  # optional, defaults to localhost:11434
)
```

### OpenRouter

```python
# Set environment variable
export OPENROUTER_API_KEY=your-key

dataset = engine.create_data(
    model_name="anthropic/claude-3.5-sonnet",
    num_steps=10,
    api_provider=APIProvider.OPENROUTER
)
```

### Custom OpenAI-Compatible APIs

```python
dataset = engine.create_data(
    model_name="custom-model",
    num_steps=10,
    api_provider=APIProvider.OPENAI_COMPATIBLE,
    api_base="http://your-server.com/v1",
    api_key="your-api-key"
)
```

## API Reference

### Core Classes

#### `DataEngine(args: EngineArguments)`
Main class for data generation.

**Methods:**
- `create_data(model_name, num_steps, batch_size=10, topic_tree=None, api_provider=APIProvider.DEFAULT, api_base=None, api_key=None)` - Generate synthetic data

#### `EngineArguments`
Configuration for data generation.

**Parameters:**
- `instructions: str` - Instructions for the model on what type of data to generate
- `system_prompt: str` - System prompt for the model
- `example_data: Dataset = None` - Optional example data to guide generation

#### `TopicTree(args: TopicTreeArguments)`  
Creates hierarchical topic structures for diverse data generation.

**Methods:**
- `build_tree(model_name)` - Build the topic tree using specified model
- `save(filename)` - Save topic tree to JSONL file

#### `TopicTreeArguments`
Configuration for topic tree generation.

**Parameters:**
- `root_prompt: str` - Root topic prompt
- `tree_degree: int = 10` - Number of subtopics per node
- `tree_depth: int = 3` - Depth of the tree
- `api_provider: APIProvider = APIProvider.DEFAULT` - API provider for tree generation
- `api_base: str = None` - Custom API base URL
- `api_key: str = None` - API key

#### `APIProvider` (Enum)
- `DEFAULT` - OpenAI, Azure OpenAI, etc.
- `OLLAMA` - Local Ollama models  
- `OPENAI_COMPATIBLE` - Custom OpenAI-compatible APIs
- `OPENROUTER` - OpenRouter platform

### Dataset Format

Generated datasets use OpenAI's chat format:

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

This format is compatible with:
- OpenAI fine-tuning API
- Most open-source training frameworks
- Popular training libraries like FastChat

## Environment Variables

- `OPENAI_API_KEY` - For OpenAI/Azure OpenAI
- `OPENROUTER_API_KEY` - For OpenRouter

## License

MIT License - see LICENSE file for details.