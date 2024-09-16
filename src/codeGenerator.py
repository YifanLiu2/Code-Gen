import json, copy
from typing import Optional
from src.llm import LLM

# PROMPT_TYPE = {"Clear Prompt", "Ambiguous Prompt", "Incomplete Information Prompt",}
PROMPT_TYPE = {"Original NL Prompt"}

ADDITIONAL_REQUIREMENTS = """
Additional Requirements:
-- Ensure your output includes only the function body.
-- Ensure that the first line of function body is indented with four spaces.
-- Do not define any helper functions before starting the main function body. All helper functions must be defined within the function body you are asked to write.
"""

class CodeGenerator:
    """
     A class that generates Python code based on a set of prompts.
    """
    def __init__(self, agent: LLM) -> None:
        self.agent = agent

    def generate_code(self, prompt: str, message: Optional[list[dict]] = None) -> tuple[str, list[dict]]:
        """
        Generates Python code based on the given prompt and an optional message context.

        prompt (str): The prompt to generate code for.
        message (Optional[List[Dict[str, any]]]): Additional contextual information provided as a list of dictionaries.
        """
        # create default prompt
        system_prompt = f"""
        You are a code generator. 
    
        Complete the function body based on the provided functional signature by the user and other optional interaction histroy, with following requirements:
        - Ensure your output includes only the function body, omitting any functional signatures, docstrings, and external comments.
        - The output should be formatted as a JSON object, with the key "solution". This key should contain the generated Python function body as a properly escaped string. 
        - Ensure that the first line of function body is indented with four spaces.
        - Do not define any helper functions before starting the main function body. All helper functions must be defined within the function body you are asked to write.
        """
        if message is None:
            message = [
                {"role": "system", "content": system_prompt},
            ]
        
        user_prompt = {"role": "user", "content": f"{prompt}\n{ADDITIONAL_REQUIREMENTS}"}

        # append new user question
        message_copy = copy.deepcopy(message)
        message_copy.append(user_prompt)

        # run agent
        response = self.agent.generate(message=message_copy)
        start = response.find("{")
        end = response.rfind("}") + 1
        solution_json = response[start:end]
        solution = json.loads(solution_json)["solution"]

        # append assistant response
        message_copy.append({"role": "assistant", "content": response})

        return solution, message_copy
    