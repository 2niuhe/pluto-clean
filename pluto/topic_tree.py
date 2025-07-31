import litellm
import json
from dataclasses import dataclass
import uuid
import os
from typing import List, Optional
from .utils import extract_list
from .prompts import TREE_GENERATION_PROMPT
from .types import APIProvider


@dataclass
class TopicTreeArguments:
    root_prompt: str
    model_system_prompt: str = None
    tree_degree: int = 10
    tree_depth: int = 3
    # API 提供商配置
    api_provider: APIProvider = APIProvider.DEFAULT
    api_base: Optional[str] = None
    api_key: Optional[str] = None


class TopicTree:
    def __init__(self, args: TopicTreeArguments):
        self.args = args
        self.tree_paths = []

    def build_tree(self, model_name: str = "gpt-3.5-turbo-1106"):
        build_id = uuid.uuid4()
        self.tree_paths = self.build_subtree(
            model_name,
            [self.args.root_prompt],
            self.args.model_system_prompt,
            self.args.tree_degree,
            self.args.tree_depth,
        )

    def build_subtree(
        self,
        model_name: str,
        node_path: List[str],
        system_prompt: str,
        tree_degree: int,
        subtree_depth: int,
    ):
        print(f"building subtree for path: {' -> '.join(node_path)}")
        if subtree_depth == 0:
            return [node_path]

        else:
            subnodes = self.get_subtopics(
                system_prompt=system_prompt,
                node_path=node_path,
                num_subtopics=tree_degree,
                model_name=model_name,
            )
            updated_node_paths = [node_path + [sub] for sub in subnodes]
            result = []
            for path in updated_node_paths:
                result.extend(
                    self.build_subtree(
                        model_name, path, system_prompt, tree_degree, subtree_depth - 1
                    )
                )
            return result

    def get_subtopics(
        self,
        system_prompt: str,
        node_path: List[str],
        num_subtopics: int,
        model_name: str,
    ):
        prompt = TREE_GENERATION_PROMPT

        prompt = prompt.replace("{{{{system_prompt}}}}", system_prompt)
        prompt = prompt.replace("{{{{subtopics_list}}}}", " -> ".join(node_path))
        prompt = prompt.replace("{{{{num_subtopics}}}}", str(num_subtopics))

        # 根据 API 提供商配置模型名称和参数
        final_model_name, final_api_base, final_api_key = self._configure_api_provider(
            model_name, self.args.api_provider, self.args.api_base, self.args.api_key
        )

        # 构建参数
        completion_params = {
            "model": final_model_name,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }

        # 根据 API 提供商添加特定参数
        if final_api_base:
            completion_params["api_base"] = final_api_base
        if final_api_key:
            completion_params["api_key"] = final_api_key

        response = litellm.completion(**completion_params)

        return extract_list(response.choices[0].message.content)

    def save(self, save_path: str):
        with open(save_path, "w", encoding="utf-8") as f:
            for path in self.tree_paths:
                f.write(json.dumps(dict(path=path), ensure_ascii=False) + "\n")

    def _configure_api_provider(
        self,
        model_name: str,
        api_provider: APIProvider,
        api_base: Optional[str],
        api_key: Optional[str],
    ):
        """根据 API 提供商配置模型名称和参数"""

        if api_provider == APIProvider.OLLAMA:
            # Ollama 配置
            final_model_name = f"ollama/{model_name}"
            final_api_base = api_base or "http://localhost:11434"
            final_api_key = api_key  # Ollama 通常不需要 API key

        elif api_provider == APIProvider.OPENAI_COMPATIBLE:
            # 自定义 base URL 的 OpenAI 兼容接口
            final_model_name = f"openai/{model_name}"
            final_api_base = api_base
            final_api_key = api_key

            if not final_api_base:
                raise ValueError("api_base is required for OpenAI compatible provider")
            if not final_api_key:
                raise ValueError("api_key is required for OpenAI compatible provider")

        elif api_provider == APIProvider.OPENROUTER:
            # OpenRouter 配置
            final_model_name = f"openrouter/{model_name}"
            final_api_base = api_base or "https://openrouter.ai/api/v1"
            final_api_key = api_key

            if not final_api_key:
                # 尝试从环境变量获取
                final_api_key = os.getenv("OPENROUTER_API_KEY")
                if not final_api_key:
                    raise ValueError(
                        "api_key or OPENROUTER_API_KEY environment variable is required for OpenRouter provider"
                    )

        else:  # APIProvider.DEFAULT
            # 默认配置（OpenAI/Azure 等）
            final_model_name = model_name
            final_api_base = api_base
            final_api_key = api_key

        return final_model_name, final_api_base, final_api_key
