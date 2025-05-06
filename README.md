# MCV Conversation generator

This repository serves the datasets used in the main project along with the relevant tools to generate and format new datasets of any given size.

# Setup

1. Python 3.x is required.
2. `python -m venv venv`
3. a. `source venv/bin/activate` (Linux)
   b.`C:/Full/path/to/venv/Scripts/Activate.ps1` (Windows Powershell)
4. `(venv) pip install -r requirements.txt`

# Usage

```bash
(venv) python generate.py
(venv) python format.py
```

This will produce your `1k_minecraft_villager_dataset_tokens_6-llama.json` and `1k_minecraft_villager_dataset_formatted_6-llama.jsonl` in the `datasets` directory (by default)