FORMAT = "llama"  # Format to convert the dataset to (llama or olmo)
ID = 2  # Unique ID for the formatted dataset (e.g., 1, 2, 3, ...)
INPUT_DATASET = "10k_minecraft_villager_dataset.json"
OUTPUT_DATASET = f"{INPUT_DATASET.split('.')[0]}_formatted_{ID}-{FORMAT}.jsonl"
TOKEN_FILE = f"{INPUT_DATASET.split('.')[0]}_tokens_{ID}-{FORMAT}.json"

import json
from tqdm import tqdm


"""Converts a conversation into Llama 3.1 format"""
def format_conversation_llama(conversation):
    system_message = f"<|start_header_id|>system<|end_header_id|>\nYou have a {conversation['personality']} personality."
    chat_messages = ["<|begin_of_text|>\n", system_message]

    for step in conversation["steps"]:
        role = step["role"]
        action = step["action"]

        # Determine user/assistant role
        header = "<|start_header_id|>user<|end_header_id|>" if role == "player" else "<|start_header_id|>assistant<|end_header_id|>"

        # Handle different actions
        if action == "speak":
            content = f"<<speak>> {step['content']}"
        elif action == "offer":
            content = f"<<offer>> <item> {step['item']} <price> {step['price']} <currency> {step['currency']}"
        elif action == "give":
            content = f"<<give>> <item> {step['item']}"
        else:
            content = f"<<{action}>>"

        # Append formatted message with correct spacing
        chat_messages.append(f"\n{header}\n{content}")

    chat_messages.append("\n<|end_of_text|>")
    return "\n".join(chat_messages)

# Function to process each conversation and convert to the desired format
def process_conversations(input_file, output_file, token_file):
    # Open the output JSONL and special tokens file in append mode
    with open(output_file, 'w') as out_f, open(token_file, 'w') as token_f:
        special_tokens = set()  # Set to hold unique special tokens

        # Open the input file and process in a memory-efficient manner
        with open(input_file, 'r') as f:
            data = json.load(f)  # Read the entire JSON content (if too large, consider streaming it line by line)
            convos = []

            # Use tqdm to show progress bar over all conversations
            for conv in tqdm(data["conversations"], desc="Processing Conversations"):
                # steps = conv["steps"]

                # # Iterate through each step to create input/output pairs
                # for i in range(len(steps)):  # Stop before the last step
                #     step = steps[i]

                #     content = f""

                #     # Check if 'content' exists in the current step
                #     if 'content' in current_step:
                #         input_text = f"<|{current_step['role']}|> <|{current_step['action']}|> {current_step['content']}"
                #     else:
                #         input_text = f"<|{current_step['role']}|> <|{current_step['action']}|>"

                #     # Check if 'content' exists in the next step
                #     if 'content' in next_step:
                #         output_text = f"<|{next_step['role']}|> <|{next_step['action']}|> {next_step['content']}"
                #     else:
                #         output_text = f"<|{next_step['role']}|> <|{next_step['action']}|>"

                #     # Add special tokens to the set
                #     special_tokens.add(f"<|{current_step['role']}|>")
                #     special_tokens.add(f"<|{next_step['role']}|>")
                #     special_tokens.add(f"<|{current_step['action']}|>")
                #     special_tokens.add(f"<|{next_step['action']}|>")

                #     # Add item, price, and currency to output if present
                #     if 'item' in next_step:
                #         output_text += f" <|item|> {next_step['item']}"
                #         special_tokens.add("<|item|>")
                #     if 'price' in next_step:
                #         output_text += f" <|price|> {next_step['price']}"
                #         special_tokens.add("<|price|>")
                #     if 'currency' in next_step:
                #         output_text += f" <|currency|> {next_step['currency']}"
                #         special_tokens.add("<|currency|>")

                #     # Write the input-output pair to the JSONL file
                #     json.dump({"input": input_text.strip(), "output": output_text.strip()}, out_f)
                #     out_f.write("\n")
                convos.append(format_conversation_llama(conv))

        # Write all special tokens to the token file (writing only once at the end)
        out_f.write("\n\n".join(convos))
        special_tokens = [
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
        ]
        json.dump(list(special_tokens), token_f)

# Run the function to process the conversations
process_conversations(INPUT_DATASET, OUTPUT_DATASET, TOKEN_FILE)

print(f"Conversion complete. Check '{OUTPUT_DATASET}' and '{TOKEN_FILE}'.")
