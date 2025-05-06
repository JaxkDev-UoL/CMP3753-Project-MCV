FORMAT = "llama"  # Format to convert the dataset to (llama or olmo)
ID = 3  # Unique ID for the formatted dataset (e.g., 1, 2, 3, ...)
INPUT_DATASET = "100_minecraft_villager_dataset.json"
OUTPUT_DATASET = f"{INPUT_DATASET.split('.')[0]}_formatted_{ID}-{FORMAT}.txt"
TOKEN_FILE = f"{INPUT_DATASET.split('.')[0]}_tokens_{ID}-{FORMAT}.json"

import json
from tqdm import tqdm

"""Converts a conversation into Llama 3.1 format"""
def format_conversation_llama(conversation):
    system_message = f"<|start_header_id|>system<|end_header_id|>\nYou have a {conversation['personality']} personality."
    chat_messages = ["<|begin_of_text|>\n", system_message]

    for i in range(len(conversation["steps"])):
        step = conversation["steps"][i]
        if i < len(conversation["steps"]) - 1:
            next_step = conversation["steps"][i + 1]
            if next_step["role"] != step["role"]:
                eot = "<|eot_id|>"
            else:
                eot = ""
        else:
            eot = "<|eot_id|>"

        role = step["role"]
        action = step["action"]

        # Determine user/assistant role
        header = "<|start_header_id|>user<|end_header_id|>" if role == "player" else "<|start_header_id|>assistant<|end_header_id|>"

        # Handle different actions
        if action == "speak":
            content = f"<<speak>> {step['content']}" if step["content"] else "<<speak>>"
        elif action == "offer":
            content = f"<<offer>> <item> {step['item']} <price> {step['price']} <currency> {step['currency']}"
        elif action == "give":
            content = f"<<give>> <item> {step['item']}"
        elif action == "grumble":
            content = "<<grumble>>"
        elif action == "wave":
            content = "<<wave>>"
        elif action == "leave":
            content = "<<leave>>"
        elif action == "ignore":
            content = "<<ignore>>"
        else:
            content = f"<<{action}>>"


        # Append formatted message with correct spacing
        chat_messages.append(f"\n{header.strip()}\n{content.strip()}{eot}")

    chat_messages.append("\n<|end_of_text|>")
    return "\n".join(chat_messages)

# Function to process each conversation and convert to the desired format
def process_conversations(input_file, output_file, token_file):
    with open(output_file, 'w') as out_f, open(token_file, 'w') as token_f:
        special_tokens = set([
            "<<give>>",
            "<<wave>>",
            "<<leave>>",
            "<item>",
            "<<speak>>",
            "<<grumble>>",
            "<currency>",
            "<<ignore>>",
            "<price>",
            "<<offer>>"
        ])

        with open(input_file, 'r') as f:
            data = json.load(f)  # Read full JSON (consider streaming if too large)
            convos = [format_conversation_llama(conv) for conv in tqdm(data["conversations"], desc="Processing Conversations")]

        # Write all formatted conversations to file
        out_f.write("\n\n".join(convos))

        # Write special tokens to token file
        json.dump(sorted(special_tokens), token_f)

# Run the function to process the conversations
process_conversations(INPUT_DATASET, OUTPUT_DATASET, TOKEN_FILE)

print(f"Conversion complete. Check '{OUTPUT_DATASET}' and '{TOKEN_FILE}'.")
