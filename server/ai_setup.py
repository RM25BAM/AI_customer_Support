import requests
import json
import os
from dotenv import load_dotenv
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


load_dotenv('server/.env.dev')

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')

class LLAMA2LLM(LLM):
    n: int

    @property
    def _llm_type(self) -> str:
        return "claude2"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': "meta-llama/llama-3.1-8b-instruct:free",
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, data=json.dumps(data))
        output = response.json()['choices'][0]['message']['content']

        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return output

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"n": self.n}

llm = LLAMA2LLM(n=1)

