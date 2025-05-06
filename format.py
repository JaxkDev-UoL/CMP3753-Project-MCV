import json
from tqdm import tqdm

FORMAT = "llama"  # Format to convert the dataset to (llama or olmo -- OLMO NOT SUPPORTED NOW)
ID = 6  # Unique ID for the formatted dataset (e.g., 1, 2, 3, ...) -- INCREMENT THIS FOR EACH NEW VERSION
INPUT_DATASET = "datasets/1k_minecraft_villager_dataset.json"


### EDIT ABOVE THIS LINE ONLY ###


OUTPUT_DATASET = f"{INPUT_DATASET.split('.')[0]}_formatted_{ID}-{FORMAT}.jsonl"
TOKEN_FILE = f"{INPUT_DATASET.split('.')[0]}_tokens_{ID}-{FORMAT}.json"

"""Converts a conversation into Llama 3.1 format"""
def format_conversation_llama(conversation):
    messages = []

    for i in range(len(conversation["steps"])):
        step = conversation["steps"][i]
        prev = ""

        # Merge all sequential assistant messages into a single message, same for user messages into this one content
        j = i - 1
        if j >= 0 and conversation["steps"][j]["role"] == step["role"]:
            prev = messages.pop()[1] + "\n"

        action = step["action"]
        # Determine correct user/assistant role (not villager...)
        user = "user" if step["role"] == "player" else "assistant"

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
        messages.append([user, (prev + content).strip()])

    if messages[0][0] == "assistant":
        messages.remove(messages[0])
    if messages[-1][0] == "user":
        messages.remove(messages[-1])

    new_messages = []
    for i in range(0, len(messages)-1, 2):
        # Join user and assistant messages
        new_messages.append({'user': messages[i][1], 'assistant': messages[i + 1][1]})

    return new_messages


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
            data = json.load(f)  # Read full JSON (may consider streaming if this gets way too large)
            convos = [format_conversation_llama(conv) for conv in tqdm(data["conversations"], desc="Processing Conversations")]

        # Write all formatted conversations to file
        # Each line is a JSON object representing a conversation
        for conv in convos:
            out_f.write(json.dumps(conv) + "\n")

        # Write special tokens to token file
        json.dump(sorted(special_tokens), token_f)


process_conversations(INPUT_DATASET, OUTPUT_DATASET, TOKEN_FILE)

print(f"Conversion complete. Check '{OUTPUT_DATASET}' and '{TOKEN_FILE}'.")
