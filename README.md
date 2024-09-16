# Code Gen
This repository contains the code for the paper 'Enhancing Code Generation in Interactive Systems with Additional User Information.'

Poster of this project is available at [this link](poster.pdf).

## Set up

Run the following command to install the required packages:
```bash
pip install -r requirements.txt
```

Next, add your OpenAI API key to the `config.py`.

## Code
The `src/codeGeneration.py` handles the first-pass code generation using the provided LLM.

The `src/codeFix.py` is responsible for code fixing, utilizing the fixing templates from the `data` section.
