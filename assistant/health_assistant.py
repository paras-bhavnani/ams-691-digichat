import json
import logging
from typing import Optional

import openai

from assistant.function_parser import parse_function_to_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_MESSAGE = """
This AI Assistant is a sophisticated software system powered by advanced language models.

Specializing in health, fitness, and nutrition tasks, the Assistant offers calculations for health metrics like Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) using established equations. It can also retrieve nutritional information for various food items via external APIs.

The Assistant engages in meaningful conversations about health and nutrition, providing helpful responses and critical health metric values. This allows users to gain a better understanding of their energy expenditure and nutritional intake.

Continuously evolving, the Assistant improves its ability to provide accurate and informative responses. It processes large amounts of text, generates human-like responses, and offers detailed explanations about complex health metrics.

Whether you need to understand your daily energy expenditure, calculate your BMR, or obtain nutritional information about your meals, this Assistant is here to help. The primary goal is to promote a healthier lifestyle by making nutritional and metabolic information more accessible.
"""

class HealthAssistant:
    def __init__(
        self,
        openai_api_key: str,
        model_name: str = 'gpt-4-0613',
        custom_functions: Optional[list] = None
    ):
        openai.api_key = openai_api_key
        self.model_name = model_name
        self.custom_functions = self._process_custom_functions(custom_functions)
        self.function_registry = self._create_function_registry(custom_functions)
        self.conversation_history = [{'role': 'system', 'content': SYSTEM_MESSAGE}]

    def _process_custom_functions(self, functions: Optional[list]) -> Optional[list]:
        if not functions:
            return None
        return [parse_function_to_schema(func) for func in functions]

    def _create_function_registry(self, functions: Optional[list]) -> dict:
        if not functions:
            return {}
        return {func.__name__: func for func in functions}

    def _generate_ai_response(
        self, messages: list, use_functions: bool = True
    ) -> openai.ChatCompletion:
        if use_functions and self.custom_functions:
            return openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                functions=self.custom_functions
            )
        return openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages
        )

    def _process_response(self) -> openai.ChatCompletion:
        internal_thoughts = []
        while True:
            print('.', end='', flush=True)
            response = self._generate_ai_response(
                self.conversation_history + internal_thoughts
            )

            outcome = response.choices[0].finish_reason
            if outcome == 'stop' or len(internal_thoughts) > 3:
                final_thought = self._construct_final_answer(internal_thoughts)
                final_response = self._generate_ai_response(
                    self.conversation_history + [final_thought],
                    use_functions=False
                )
                return final_response
            elif outcome == 'function_call':
                self._handle_function_execution(response, internal_thoughts)
            else:
                raise ValueError(f"Unexpected outcome: {outcome}")

    def _handle_function_execution(self, response: openai.ChatCompletion, internal_thoughts: list):
        internal_thoughts.append(response.choices[0].message.to_dict())
        func_name = response.choices[0].message.function_call.name
        args_json = response.choices[0].message.function_call.arguments
        result = self._execute_function(func_name, args_json)
        result_msg = {'role': 'assistant', 'content': f"Function result: {result}"}
        internal_thoughts.append(result_msg)

    def _execute_function(self, func_name: str, args_json: str):
        args = json.loads(args_json)
        logger.info(f"Executing function: {func_name}")
        logger.info(f"Arguments: {args}")
        func = self.function_registry[func_name]
        logger.info(f"Function object: {func}")
        result = func(**args)
        return result

    def _construct_final_answer(self, internal_thoughts: list):
        thought_process = "To answer the query, I will follow these steps:\n\n"
        for thought in internal_thoughts:
            if 'function_call' in thought:
                thought_process += (f"I will use the {thought['function_call']['name']} "
                                    f"function with arguments: {thought['function_call']['arguments']}\n\n")
            else:
                thought_process += f"{thought['content']}\n\n"
        
        return {
            'role': 'assistant',
            'content': (f"{thought_process} Based on this analysis, I will now formulate "
                        "the response, assuming the user hasn't seen this thought process.")
        }

    def ask(self, query: str) -> openai.ChatCompletion:
        self.conversation_history.append({'role': 'user', 'content': query})
        response = self._process_response()
        self.conversation_history.append(response.choices[0].message.to_dict())
        return response
