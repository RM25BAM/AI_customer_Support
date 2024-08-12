import requests
import json
import os
from dotenv import load_dotenv
from typing import Any, List, Mapping, Optional
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
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

def respond(survey):
    response_schemas = [
        ResponseSchema(
            name="Goal",
            description=f"The gym goal is '{survey['What is the gym goal']}'. Generate a schedule that aligns with this goal while considering the user's class schedule."
        ),
        ResponseSchema(
            name="FreeTime",
            description=f"The user has '{survey['How much free time you have']}' each week. Consider this when generating the exercise schedule."
        ),
        ResponseSchema(
            name="ClassSchedule",
            description=f"The user's weekly class schedule is '{survey['What is your weekly schedule looks like']}'. Ensure the exercise schedule does not conflict with this."
        ),
        ResponseSchema(
            name="Weight",
            description=f"The user's current weight is '{survey['What is your current weight?']}'. Take this into account when generating the exercise schedule."
        ),
        ResponseSchema(
            name="Height",
            description=f"The user's height is '{survey['What is your height?']}'. Consider this when generating the exercise schedule."
        ),
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=("Generate a schedule with gym exercises for 7 days considering the user's goals, free time, class "
                  "schedule, weight, height, wakeup time, and meal times.\n"
                  "Ensure that the output is in the following JSON format:\n"
                  "{format_instructions}\n\n"
                  "User data: {user_data}"),
        input_variables=["user_data"],
        partial_variables={"format_instructions": format_instructions},
    )

    chain = prompt | llm | output_parser

    user_data = {
        "gym_goal": "Lose weight",
        "free_time": "10 hours per week",
        "class_schedule": {
            "Monday": "9:00 AM - 10:30 AM (Math), 2:00 PM - 3:30 PM (History)",
            "Tuesday": "10:00 AM - 11:30 AM (Physics), 1:00 PM - 2:30 PM (Chemistry)",
            "Wednesday": "9:00 AM - 10:30 AM (Math), 2:00 PM - 3:30 PM (History)",
            "Thursday": "10:00 AM - 11:30 AM (Physics), 1:00 PM - 2:30 PM (Chemistry)",
            "Friday": "9:00 AM - 10:30 AM (English), 2:00 PM - 3:30 PM (Biology)",
        },
        "weight": "70 kg",
        "height": "170 cm",
    }

    response = chain.invoke({"user_data": user_data})

    return response