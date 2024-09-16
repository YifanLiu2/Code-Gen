import json, os, argparse
from tqdm import tqdm
import pandas as pd
from src.llm import *

DEFAULT_COLUMNS = {"task_id", "prompt", "entry_point"}
with open("data/curated_data/prompts_v4.json", "r") as prompt:
    data = json.load(prompt)
    OG_PROMPT = {key: value["Original NL Prompt"] for key, value in data.items()}

class PromptAgent():
    """
    A class designed to extract and transform function docstrings based on various predefined prompt types stored in the PROMPT_TYPE dictionary.
    """

    def __init__(self, input_path: str, output_path: str, agent: LLM, temperature: int = 0) -> None:
        if temperature:
            if temperature <= 0:
                raise ValueError(f"Invalid temperature, must be non-negative: {temperature}")
            
        # check valid input data path
        if not os.path.exists(input_path) or not input_path.endswith(".csv"):
            raise ValueError(f"Invalid input data path, must be a .csv file: {input_path}")
        
        # check output data path
        if not output_path.endswith(".json"):
            raise ValueError(f"Invalid output data path, must be a .json file: {output_path}")
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # set
        self.dataset = pd.read_csv(input_path)
        for column in DEFAULT_COLUMNS:
            if column not in self.dataset:
                raise ValueError(f"Invalid dataset, \"{column}\" column not found")

        self.output_path = output_path
        self.agent = agent
        self.temperature = temperature


    def process_prompt(self) -> None:
        """
        Processes each prompt in the dataset.
        """
        results = dict()

        # extract prompt and handle error
        task_ids = self.dataset["task_id"]
        entry_points = self.dataset["entry_point"]

        for task, entry_point in tqdm(zip(task_ids, entry_points), total=len(task_ids), desc="Processing Prompts"):
            try:
                og_prompt = OG_PROMPT[task]
                new_prompts = self.paraphrase(original_prompt=og_prompt, function_name=entry_point)
            except Exception as e:
                print(f"Error processing {task}: {e}")
                continue

            results[task] = new_prompts
        
        # save results
        with open(self.output_path, "w") as f:
            json.dump(results, f, indent=4)


    def paraphrase(self, original_prompt: str, function_name: str) -> dict:
        """
        Paraphrase the original function's docstring into a series of new docstrings according to various predefined categories in the FAILURE_TYPE dictionary.
        
        original_prompt (str): The current docstring of the function.
        function_name (str): The name of the function whose docstring is to be transformed.
        """
        prompt_text = """
        Your task is to paraphrase the docstring of the function {function_name}. Please follow the instructions below:
            - Keep all other components unchanged, including the function signature, import statements, and any helper methods. Only replace the entire original docstring with the new one.
            - The output should be in JSON format, with the key 'paraphrase' and the value being a string containing the paraphrased docstring.
        
        Prompt:
        {original_prompt}
        """

        message = [
            {"role": "system", "content": "You are a software engineer."},
            {"role": "user", "content": prompt_text.format(function_name="below_zero", original_prompt="from typing import List\n\ndef below_zero(operations: List[int]) -> bool:\\n    \"\"\" You're given a list of deposit and withdrawal operations on a bank account that starts with zero balance. Your task is to detect if at any point the balance of account falls below zero, and at that point function should return True. Otherwise it should return False.\\n    \"\"\"")}, 
            {"role": "system", "content": """{"paraphrase": "from typing import List\n\ndef below_zero(operations: List[int]) -> bool:\n    \"\"\"Analyze a sequence of banking transactions (deposits and withdrawals) starting from a balance of zero. Determine whether the account's balance goes negative at any point during the transactions. If the balance becomes negative, the function should return True; if not, it remains False.\"\"\""}"""},
            {"role": "user", "content": prompt_text.format(function_name=function_name, original_prompt=original_prompt)}, 
        ]

        # generate response
        response = self.agent.generate(message=message, temperature=self.temperature)

        # parse results
        start = response.find("{")
        end = response.rfind("}") + 1
        solution_json = response[start:end]
        new_prompts = json.loads(solution_json)[""]
            
        return new_prompts






    response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "answers",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                    "parameters": {
                        "type": "string"
                    },
                    "return": {
                        "type": "string"
                    }
                    },
                    "required": ["parameters", "return"],
                    "additionalProperties": False
                }
                }
            }

    def parameter(self, original_prompt: str, function_name: str) -> dict:
        """
        Paraphrase the original function's docstring into a series of new docstrings according to various predefined categories in the FAILURE_TYPE dictionary.
        
        original_prompt (str): The current docstring of the function.
        function_name (str): The name of the function whose docstring is to be transformed.
        """
        prompt_text = """
        Your task is to provide descriptions of the parameters and return values for the function {function_name}. Please follow the instructions below:
            - List each parameter in the format parameter name (data type): description. 
            - Describe the return value, including its data type.
            - The output should be in JSON format, with the key 'parameters' and 'return'.
        
        Prompt:
        {original_prompt}
        """

        message = [
            {"role": "system", "content": "You are a software engineer."},
            # {"role": "user", "content": prompt_text.format(function_name="below_zero", original_prompt="from typing import List\n\ndef below_zero(operations: List[int]) -> bool:\\n    \"\"\" You're given a list of deposit and withdrawal operations on a bank account that starts with zero balance. Your task is to detect if at any point the balance of account falls below zero, and at that point function should return True. Otherwise it should return False.\\n    \"\"\"")}, 
            # {"role": "system", "content": """{"paraphrase": "from typing import List\n\ndef below_zero(operations: List[int]) -> bool:\n    \"\"\"Analyze a sequence of banking transactions (deposits and withdrawals) starting from a balance of zero. Determine whether the account's balance goes negative at any point during the transactions. If the balance becomes negative, the function should return True; if not, it remains False.\"\"\""}"""},
            {"role": "user", "content": prompt_text.format(function_name=function_name, original_prompt=original_prompt)}, 
        ]

        # generate response
        response = self.agent.generate(message=message, temperature=self.temperature)


        # parse results
        start = response.find("{")
        end = response.rfind("}") + 1
        solution_json = response[start:end]
        param = json.loads(solution_json)["parameters"]
        return_ = json.loads(solution_json)["return"]
            
        return param, return_


    def process_prompt(self) -> None:
        """
        Processes each prompt in the dataset.
        """
        results = dict()

        # extract prompt and handle error
        task_ids = self.dataset["task_id"]
        prompt = self.dataset["prompt"]
        entry_points = self.dataset["entry_point"]

        for task, entry_point in tqdm(zip(task_ids, entry_points), total=len(task_ids), desc="Processing Prompts"):
            try:
                param, return_ = self.parameter(original_prompt=prompt, function_name=entry_point)
            except Exception as e:
                print(f"Error processing {task}: {e}")
                continue

            results[task] = {"param": param, "return": return_}
        
        # save results
        with open(self.output_path, "w") as f:
            json.dump(results, f, indent=4)



def main(parser):
    args = parser.parse_args()
    agent = GPTChat()
    extractor = PromptAgent(input_path=args.input_path, output_path=args.output_path, agent=agent)
    extractor.process_prompt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some prompts.")
    parser.add_argument('--input_path', type=str, default="data/eval_data/test.csv",
                        help='Path to the input data file')
    parser.add_argument('--output_path', type=str, default="data/curated_data/prompts.json",
                        help='Path to the output data file')
    parser.add_argument('--temperature', type=float, default=0,
                        help='temperature of the llm.')

    main(parser)


