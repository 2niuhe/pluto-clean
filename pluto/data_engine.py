import litellm
from typing import List, Optional, Tuple
from tqdm import tqdm
import random
import json
import math
from dataclasses import dataclass
from .prompts import SAMPLE_GENERATION_PROMPT
from .topic_tree import TopicTree
from .dataset import Dataset
from .types import APIProvider


@dataclass
class EngineArguments:
    instructions: str
    system_prompt: str
    example_data: Optional[Dataset] = None


class DataEngine:
    def __init__(self, args: EngineArguments):
        self.args = args
        self.dataset = Dataset()

    def create_data(
        self,
        model_name: str,
        num_steps: Optional[int] = None,
        num_example_demonstrations: int = 3,
        batch_size: int = 10,
        topic_tree: Optional[TopicTree] = None,
        api_provider: APIProvider = APIProvider.DEFAULT,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Dataset:
        data_creation_prompt = SAMPLE_GENERATION_PROMPT

        # 根据 API 提供商配置模型名称和参数
        final_model_name, final_api_base, final_api_key = self._configure_api_provider(
            model_name, api_provider, api_base, api_key
        )

        if self.args.example_data is None:
            num_example_demonstrations = 0

        if num_steps is None:
            raise Exception("no number of steps was specified")

        if topic_tree is not None:
            tree_paths = topic_tree.tree_paths

        if topic_tree is not None and num_steps is not None:
            if num_steps * batch_size > len(tree_paths):
                raise Exception(
                    "num_steps * batch_size cannot be bigger than number of tree paths"
                )
            else:
                tree_paths = random.sample(tree_paths, num_steps * batch_size)

        if topic_tree is not None:
            num_steps = math.ceil(len(tree_paths) / batch_size)

        print(f"Generating dataset in {num_steps} steps, with batch size {batch_size}.")
        for step in tqdm(range(num_steps)):
            prompts = []
            for i in range(batch_size):
                if topic_tree is not None:
                    try:
                        path = tree_paths[step * batch_size + i]
                    except Exception:
                        break
                else:
                    path = None

                sample_prompt = self.build_prompt(
                    data_creation_prompt=data_creation_prompt,
                    model_name=model_name,
                    num_example_demonstrations=num_example_demonstrations,
                    subtopics_list=path,
                )
                prompts.append(sample_prompt)

            for j in range(3):
                try:
                    # 使用统一的配置调用 litellm
                    responses = litellm.batch_completion(
                        model=final_model_name,
                        messages=[[{"role": "user", "content": p}] for p in prompts],
                        temperature=1.0,
                        max_retries=10,
                        api_base=final_api_base,
                        api_key=final_api_key,
                        response_format={"type": "json_object"} if api_provider not in [APIProvider.OLLAMA] else None
                    )

                    samples = [
                        json.loads(r.choices[0].message.content) for r in responses
                    ]
                    for sample in samples:
                        new_message = {
                            "role": "system",
                            "content": self.args.system_prompt,
                        }
                        sample["messages"].insert(0, new_message)

                    self.dataset.add_samples(samples)
                    print("Example of a generated sample: ", samples[0])
                    break

                except Exception as e:
                    print(e)
                    print("error generating example, retrying...")
                    if j == 2:
                        raise Exception(
                            f"{j} consecutive errors generating training examples. Something's probably wrong."
                        )

        return self.dataset

    def build_prompt(
        self,
        data_creation_prompt: str,
        model_name: str,
        num_example_demonstrations: int,
        subtopics_list: Optional[List[str]] = None,
    ) -> str:
        prompt = data_creation_prompt.replace(
            "{{{{system_prompt}}}}", self.build_system_prompt()
        )
        prompt = prompt.replace(
            "{{{{instructions}}}}", self.build_custom_instructions_text()
        )
        prompt = prompt.replace(
            "{{{{examples}}}}", self.build_examples_text(num_example_demonstrations)
        )
        prompt = prompt.replace(
            "{{{{subtopics}}}}", self.build_subtopics_text(subtopics_list)
        )

        return prompt

    def save_dataset(self, save_path: str) -> None:
        self.dataset.save(save_path)

    def build_custom_instructions_text(self) -> str:
        if self.args.instructions is None:
            return ""
        else:
            return f"\nHere are additional instructions:\n<instructions>\n{self.args.instructions}\n</instructions>\n"

    def build_system_prompt(self) -> str:
        return self.args.system_prompt

    def build_examples_text(self, num_example_demonstrations: int) -> str:
        if self.args.example_data is None:
            return ""

        else:
            examples_text = ""
            if num_example_demonstrations > 0:
                examples_text += "Here are output examples:\n\n"
                examples = random.sample(
                    self.args.example_data.samples, num_example_demonstrations
                )

                for i, ex in enumerate(examples):
                    examples_text += f"Example {i + 1}: \n\n{ex}\n"

            return f"\nHere are output examples:\n<examples>\n{examples_text}\n</examples>\n"

    def build_subtopics_text(self, subtopic_list: Optional[List[str]]) -> str:
        if subtopic_list is None:
            return ""
        else:
            return f"\nLastly, the topic of the training data should be related to the following subtopics: {' -> '.join(subtopic_list)}"

    def _configure_api_provider(
        self,
        model_name: str,
        api_provider: APIProvider,
        api_base: Optional[str],
        api_key: Optional[str],
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """根据 API 提供商配置模型名称和参数"""
        
        final_model_name: str
        final_api_base: Optional[str]
        final_api_key: Optional[str]

        if api_provider == APIProvider.OLLAMA:
            # Ollama 配置
            final_model_name = f"ollama/{model_name}"
            final_api_base = api_base or "http://localhost:11434"
            final_api_key = api_key  # Ollama 通常不需要 API key

        elif api_provider == APIProvider.OPENAI_COMPATIBLE:
            # 自定义 base URL 的 OpenAI 兼容接口
            final_model_name = f"openai/{model_name}"
            
            if not api_base:
                raise ValueError("api_base is required for OpenAI compatible provider")
            if not api_key:
                raise ValueError("api_key is required for OpenAI compatible provider")
            final_api_base = api_base
            final_api_key = api_key

        elif api_provider == APIProvider.OPENROUTER:
            # OpenRouter 配置
            final_model_name = f"openrouter/{model_name}"
            final_api_base = api_base or "https://openrouter.ai/api/v1"
            final_api_key = api_key

            if not final_api_key:
                # 尝试从环境变量获取
                import os

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
