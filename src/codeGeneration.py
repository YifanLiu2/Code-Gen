import os, json, argparse
from tqdm import tqdm
from src.codeGenerator import PROMPT_TYPE, CodeGenerator
from src.llm import GPTChat

def generate_codes(generator: CodeGenerator, input_path: str, output_dir: str) -> None:
    """
    Generates Python code for each prompt defined in the dataset and saves the results as JSONL files in output_dir.

    input_path (str): Path to the JSON file containing the prompts.
    output_dir (str): Directory where output JSONL files should be saved.
    """
    # load task data
    with open(input_path, "r") as f:
        data = json.load(f)
    
    with open(os.path.join(output_dir, "solutions.jsonl"), 'w') as file_s, \
            open(os.path.join(output_dir, "messages.jsonl"), 'w') as file_m:

        # generate code for each task
        for task_id, prompts in tqdm(data.items(), desc=f"Generating code", unit="task"):
            try:
                solution, message = generator.generate_code(prompts)
                file_s.write(json.dumps({"task_id": task_id, "completion": solution}) + '\n')
                file_m.write(json.dumps({"task_id": task_id, "message": message}) + '\n')

            except Exception as e:
                print(f"Error processing {task_id}: {e}")
                continue 


def main(args):
    input_path = args.input_path
    output_dir = args.output_dir

    # check input and output path
    if not os.path.exists(input_path) or not input_path.endswith(".json"):
        raise ValueError(f"Invalid input data path, must be a .json file: {input_path}")
    os.makedirs(output_dir, exist_ok=True)

    # initialize
    agent = GPTChat()
    generator = CodeGenerator(agent=agent)

    # generate codes
    generate_codes(generator=generator, input_path=input_path, output_dir=output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Python code based on prompts.")
    parser.add_argument('--input_path', type=str, required=True, help="Path to the JSON file containing prompts.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save the generated JSONL files.")
    args = parser.parse_args()

    main(args)