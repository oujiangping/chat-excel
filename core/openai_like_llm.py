"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/15 14:25
*  @FileName:   openai_like_llm.py
**************************************
"""
import os

from llama_index.core.base.llms.types import LLMMetadata, MessageRole
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

CONTEXT_WINDOW = 128000

# print("所有环境变量：")
# for key, value in os.environ.items():
#     print(f"{key}: {value}")

# 如果没有设置环境变量，报错
if "OPENAI_API_BASE" not in os.environ:
    raise ValueError("OPENAI_API_BASE 环境变量未设置")

OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_MODEL_NAME = os.environ["OPENAI_MODEL_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ANALYZE_LLM_MODEL_NAME = os.environ["ANALYZE_LLM_MODEL_NAME"]


class OpenAILikeLLM(OpenAI):
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=CONTEXT_WINDOW,
            num_output=self.max_tokens or -1,
            is_chat_model=True,
            is_function_calling_model=True,
            model_name=self.model,
            system_role=MessageRole.SYSTEM,
        )

