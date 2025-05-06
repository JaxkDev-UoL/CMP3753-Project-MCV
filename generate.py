import json
import gzip
import os
import random
import tqdm

CURRENCY = "Coins"
CONVOS = 1000
OUTPUT_FILE = "datasets/1k_minecraft_villager_dataset.json"
SEED = None #2341342
GZIP = False
INDENT = 0
NEWLINE = False


### EDIT ABOVE THIS LINE ONLY ###


PERSONALITIES = {
    "greedy": {"buy_multiplier": 1.5, "sell_multiplier": 0.5},
    "generous": {"buy_multiplier": 0.75, "sell_multiplier": 1.25},
    "neutral": {"buy_multiplier": 1.0, "sell_multiplier": 1.0},
    "cautious": {"buy_multiplier": 1.2, "sell_multiplier": 0.8},
    "friendly": {"buy_multiplier": 0.9, "sell_multiplier": 1.1}
}

# Base prices for items in minecraft bedrock (1.0.0) - generated with chatgpt-4o (24/02/2025)
ITEMS = {
    # Tools (scaling based on rarity, utility, and effectiveness)
    "Diamond Sword": 100, "Iron Pickaxe": 40, "Golden Apple": 80, "Emerald": 25, "Enchanted Book": 50,
    "Bread": 5, "Potion of Healing": 25, "Saddle": 40, "Name Tag": 50, "Lantern": 15,
    "Bow": 30, "Shield": 20, "Leather Boots": 15, "Chainmail Chestplate": 50, "Rabbit Stew": 10,
    "Firework Rocket": 10, "Compass": 15, "Fishing Rod": 12, "Shears": 15, "Anvil": 60,
    "Chiseled Stone Bricks": 8, "Glowstone": 20, "Sea Lantern": 25, "Totem of Undying": 150,
    "Trident": 100, "Spyglass": 35, "Honey Bottle": 8, "Book & Quill": 20, "Enchanted Golden Apple": 200,

    # Materials
    "Iron Ingot": 20, "Gold Ingot": 25, "Diamond": 50, "Lapis Lazuli": 12, "Redstone": 10, "Coal": 5,
    "Emerald Ore": 250, "Iron Ore": 40, "Gold Ore": 50, "Diamond Ore": 100, "Lapis Ore": 25, "Redstone Ore": 20,

    # Blocks (scaled according to rarity, utility, and function)
    "Stone": 3, "Cobblestone": 2, "Wooden Planks": 4, "Bricks": 15, "Glass": 10, "Sand": 7, "Clay": 8,
    "Glowstone": 20, "Bedrock": 999, "Crafting Table": 12, "Furnace": 18, "Chest": 25, "Dispenser": 35,
    "Vines": 12, "Bookshelf": 25, "End Stone": 35, "Netherrack": 8, "Soul Sand": 10, "Nether Brick": 20,
    "Nether Quartz Block": 30, "Jukebox": 40, "Piston": 35, "Sticky Piston": 50,
    "TNT": 30, "Redstone Block": 50, "Beacon": 500, "Cactus": 15, "Sugar Cane": 10, "Ladder": 6, "Ice": 12,
    "Packed Ice": 15, "Slime Block": 50, "Mycelium": 40, "Moss Stone": 20, "Podzol": 18, "Ender Chest": 60,

    # Food (prices scaled based on utility and hunger values)
    "Cooked Porkchop": 12, "Cooked Beef": 15, "Cooked Chicken": 18, "Cooked Mutton": 12, "Cooked Rabbit": 15,
    "Steak": 15, "Apple": 5, "Carrot": 6, "Potato": 5, "Pumpkin Pie": 15, "Melon": 4, "Mushroom Stew": 6,
    "Cake": 25, "Baked Potato": 6, "Golden Carrot": 20, "Rabbit Foot": 15, "Cooked Salmon": 18,

    # Potions (scaled based on rarity and effects)
    "Potion of Regeneration": 20, "Potion of Fire Resistance": 30, "Potion of Strength": 20, 
    "Potion of Night Vision": 20, "Potion of Swiftness": 18, "Potion of Healing": 25, "Potion of Poison": 20, 
    "Potion of Water Breathing": 25, "Potion of Weakness": 20, "Splash Potion of Weakness": 25,
    "Lingering Potion of Weakness": 30, "Splash Potion of Healing": 30, "Lingering Potion of Healing": 35,

    # Miscellaneous (scaled based on utility and functionality)
    "Ender Pearl": 35, "Flint and Steel": 15, "Clock": 18, "Bucket": 12, "Water Bucket": 15, "Lava Bucket": 20,
    "Minecart": 20, "Boat": 10, "Lead": 15, "Torch": 2, "Bed": 25, "Bucket of Milk": 10, "Snowball": 3,
    "Fire Charge": 10, "Crossbow": 40, "Fletching Table": 15,
    
    # Armor (scaled based on rarity and utility)
    "Leather Helmet": 10, "Iron Helmet": 15, "Diamond Helmet": 50, "Gold Helmet": 20, "Leather Chestplate": 25,
    "Iron Chestplate": 35, "Diamond Chestplate": 75, "Gold Chestplate": 30, "Leather Leggings": 20,
    "Iron Leggings": 30, "Diamond Leggings": 60, "Gold Leggings": 25, "Leather Boots": 18, "Iron Boots": 20,
    "Diamond Boots": 50, "Gold Boots": 20
}

with open("dictionary.json", "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)

# Loads the dictionary of villager and player responses.
DICTIONARY_VILLAGER = DICTIONARY["VILLAGER"]
DICTIONARY_PLAYER = DICTIONARY["PLAYER"]

# Possible villager responses
VILLAGER_SOUNDS = [
    "grrrrr", "mmmmmm", "graaaaa", "screeee", "hmmmmm", "hehehe", "hohoho", "hmmph", "huhhh"
]

# Possible objectives
OBJECTIVES = ["trade", "sell", "buy", "talk", "ignore"]

def generate_greeting():
    # No longer uses the DICTIONARY for greetings, instead using a more randomized approach based on the type of greeting.

    common_greetings = [
        "Hello", "Hi", "Hey", "Greetings", "Good to see you", "Nice to meet you", 
        "Howdy", "What's up", "Yo", "Hey there", "Hiya", "Good day", "How's it going?", 
        "Hey, how are you?", "What's new?", "Glad to see you!", "Long time no see!"
    ]
    
    formal_greetings = [
        "Good morning", "Good afternoon", "Good evening", "Pleasure to meet you", 
        "Greetings and salutations", "It's a pleasure to see you", "I trust you're doing well", 
        "I hope your day is going well", "I'm honored to meet you", "How do you do?", 
        "I wish you well", "May your day be bright", "I hope everything is going wonderfully"
    ]
    
    casual_greetings = [
        "Yo", "Sup", "Hey there", "Howdy", "What's up", "Hey hey", "What's crackin'?", 
        "What's good?", "What's happening?", "How's life?", "Heyyyy", "What's the vibe?", 
        "How's everything?", "What's going on?", "How's the day treating you?"
    ]
    
    rare_greetings = [
        "Woah, hey there", "Well, hello", "Oh, hi", "Hey, how's it going?", "Hey, what's new?", 
        "Fancy seeing you here!", "Well, look who it is!", "Ah, greetings, wanderer!", 
        "Ah, a familiar face!", "Oh, it's you!", "Look who it is!", "Surprise, surprise!", 
        "What a pleasant surprise!", "Well, I'll be, it's you!", "How about that, it's you again!"
    ]
    
    cheerful_greetings = [
        "Hello there!", "Hey, how's everything going?", "Hey, what's happening today?", 
        "Hey, friend!", "Hey, you!", "Greetings, my friend!", "Good to see you again!", 
        "Hey, you made it!", "Ah, it's been too long!", "So happy to see you!", "Hey, stranger, how's life?", 
        "What a great day to see you!"
    ]
    
    friendly_greetings = [
        "Hey buddy!", "Hey pal!", "Hi there, friend!", "Hey, mate!", "What's going on, pal?", 
        "How's it going, mate?", "Hey, how's it been?", "Hey, how's the world treating you?", 
        "Hey, good to see ya!", "How's everything, buddy?", "Hey, good to see you, pal!"
    ]
    
    suffixes = [
        "!", "!!", " :) ", " :D ", " my friend!", " buddy!", " pal!", " mate!", " traveler!", 
        " stranger!", " dear friend!", " good soul!", " champion!", " my friend, how are you?", 
        " friend of mine!", " fellow adventurer!", " companion!", " confidant!", " buddy ol' pal!", 
        " kindred spirit!", " my old friend!", " bright soul!", " sunshine!", " my dear!", 
        " delightful one!", " my favorite person!", " always a pleasure!"
    ]
    
    # Exponential probability distribution
    greeting_type = random.choices(
        [common_greetings, formal_greetings, casual_greetings, rare_greetings, cheerful_greetings, friendly_greetings], 
        weights=[40, 15, 15, 10, 10, 10],  # Weights to make the common greetings more likely, and so on.
        k=1
    )[0]

    greeting = random.choice(greeting_type)

    suffix = random.choices(
        suffixes,
        weights=[20, 15, 10, 10, 5, 5, 5, 4, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        k=1
    )[0]
    
    return greeting + suffix

import random

def generate_goodbye():
    # No longer uses the DICTIONARY for goodbyes, instead using a more randomized approach based on the type of goodbye.

    common_goodbyes = [
        "Goodbye", "See you", "Take care", "Farewell", "Bye", "Catch you later", 
        "Until next time", "See you soon", "Take it easy", "So long", "See you later", 
        "Have a great day", "Wishing you well", "Catch you on the flip side"
    ]
    
    formal_goodbyes = [
        "It was a pleasure meeting you", "Goodbye, and take care", "Wishing you all the best", 
        "Until we meet again", "Safe travels", "I hope our paths cross again", "Farewell, my friend", 
        "It was wonderful to see you", "Wishing you the best in all your endeavors", 
        "It was an honor, goodbye", "May the future be bright for you"
    ]
    
    casual_goodbyes = [
        "Later", "See ya", "Catch you later", "Peace out", "Adios", "Bye for now", 
        "Take it easy", "Catch you soon", "Don't be a stranger", "Take care of yourself", 
        "I'll see you around", "Later, alligator", "Bye now", "See you on the flip side"
    ]
    
    heartfelt_goodbyes = [
        "I'll miss you", "Take care of yourself", "Wishing you all the best", "Good luck, my friend", 
        "Stay safe", "I'll be thinking of you", "Wishing you happiness", "Until we meet again, take care", 
        "It was truly great to see you", "Take care, I hope everything goes well for you", 
        "I hope life treats you kindly", "Stay well, and don't forget me!"
    ]
    
    humorous_goodbyes = [
        "Don't let the door hit you on the way out!", "See you never! Just kidding, take care!", 
        "Goodbye, and don't get into too much trouble!", "You're leaving? I guess I'll survive", 
        "Goodbye, don't do anything I wouldn't do!", "Catch you on the rebound!", 
        "I'm counting down the days till we meet again!", "So long, sucker! Just kidding, have fun!", 
        "Don't forget to send postcards!", "See ya later, alligator! After a while, crocodile!"
    ]
    
    kind_goodbyes = [
        "Take care, my friend", "Stay well, take it easy", "I hope everything goes well for you", 
        "Wishing you the best, always", "Until next time, be well", "Goodbye, take care of yourself", 
        "Take care, and know you'll be missed", "Sending you positive vibes, goodbye", 
        "Wishing you all the happiness in the world", "May your days be filled with joy, goodbye", 
        "I'll be rooting for you, take care"
    ]
    
    suffixes = [
        "!", "!!", " :) ", " :D ", " my friend!", " buddy!", " pal!", " mate!", " traveler!", 
        " stranger!", " dear friend!", " good soul!", " champion!", " take care, my friend!", 
        " friend of mine!", " fellow adventurer!", " companion!", " my old friend!", " kind soul!", 
        " my bright star!"
    ]
    
    # Exponential probability distribution
    goodbye_type = random.choices(
        [common_goodbyes, formal_goodbyes, casual_goodbyes, heartfelt_goodbyes, humorous_goodbyes, kind_goodbyes], 
        weights=[40, 15, 15, 10, 10, 10],  # Adjusted weights to maintain a nice balance
        k=1
    )[0]
    #print(len(suffixes))
    goodbye = random.choice(goodbye_type)
    suffix = random.choices(
        suffixes,
        weights=[20, 15, 10, 10, 5, 5, 5, 4, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1],
        k=1
    )[0]
    
    return goodbye + suffix



# Generate a randomized conversation

def generate_conversation(convo_id):
    personality = random.choice(list(PERSONALITIES.keys()))
    personality_traits = PERSONALITIES[personality]
    item, base_price = random.choice(list(ITEMS.items()))
    objective = random.choice(OBJECTIVES)
    
    # Adjust price based on villager's personality
    buy_price = round(base_price * personality_traits["buy_multiplier"]) + random.randint(-2, 3)  # Random fluctuation
    sell_price = round(base_price * personality_traits["sell_multiplier"]) + random.randint(-2, 3)
    
    conversation = {
        "id": f"{convo_id}",
        "personality": personality,
        "objective": objective,
        "steps": []
    }

    # Start with PLAYER greeting.
    if random.random() < 0.7:
        #Speak 70%
        conversation["steps"].append({"role": "player", "action": "speak", "content": generate_greeting()})# random.choice(DICTIONARY_PLAYER["GREETINGS"])})
    else:
        #Wave 30%
        conversation["steps"].append({"role": "player", "action": "wave", "content": ""})
        if random.random() < 0.1:
            # Speak after waving 10%
            conversation["steps"].append({"role": "player", "action": "speak", "content": generate_greeting()})#random.choice(DICTIONARY_PLAYER["GREETINGS"])})
    
    # Villager greeting based on objective
    if objective == "ignore":
        # Villager greet (ignore objective)
        if random.random() < 0.9:
            #No greeting 90%
            conversation["steps"].append({"role": "villager", "action": "ignore", "content": ""})
        else:
            #grumble 10%
            conversation["steps"].append({"role": "villager", "action": "grumble", "content": random.choice(VILLAGER_SOUNDS)})
    else:
        #Villager greet
        if conversation["steps"][-1]['action'] == "wave":
            if random.random() < 0.85:
                #Wave back 85%
                conversation["steps"].append({"role": "villager", "action": "wave", "content": ""})

        if random.random() < 0.75:
            #Speak 75%
            conversation["steps"].append({"role": "villager", "action": "speak", "content": generate_greeting()})#random.choice(DICTIONARY_VILLAGER["GREETINGS"][personality])})
        else:
            #Grumble 20%
            conversation["steps"].append({"role": "villager", "action": "grumble", "content": random.choice(VILLAGER_SOUNDS)})
            if random.random() < 0.8:
                #Add greeting 80%
                conversation["steps"].append({"role": "villager", "action": "speak", "content": generate_greeting()})#random.choice(DICTIONARY_VILLAGER["GREETINGS"][personality])})
            # Just grumble (20%)... no greeting

    # Either villager or player can initiate conversation here:

    if random.random() < 0.75:
        # Player initiates conversation
        conversation["steps"].append({"role": "player", "action": "speak", "content": random.choice(DICTIONARY_PLAYER["QUERY_OFFER"])})
    
    #OFFER
    conversation["steps"].append({"role": "villager", "action": "offer", "item": item, "price": f"{sell_price}", "currency": CURRENCY})
    message = random.choice(DICTIONARY_VILLAGER["OFFERS"][personality]).replace("{item}", item).replace("{price}", str(sell_price)+' '+CURRENCY)
    conversation["steps"].append({"role": "villager", "action": "speak", "content": message})

    # Player response,
    # Different percentage of acceptance based off price compared to base price
    base_percentage = 0.7
    if sell_price < base_price:
        # Add sell_price percentage * 0.2
        base_percentage = 0.7 + (0.2 * (sell_price / base_price))
    elif sell_price > base_price:
        # Subtract sell_price percentage * 0.2
        base_percentage = 0.7 - (0.5 * (sell_price / base_price))
    
    if random.random() < base_percentage:
        # Player accepts
        conversation["steps"].append({"role": "player", "action": "speak", "content": random.choice(DICTIONARY_PLAYER["ACCEPT_OFFER"]).replace("{item}", item).replace("{price}", str(sell_price)+' '+CURRENCY)})
        # Player hands over the currency
        conversation["steps"].append({"role": "player", "action": "give", "item": f"{sell_price} {CURRENCY}"})
        # Villager gives the item
        conversation["steps"].append({"role": "villager", "action": "give", "item": item})
        # Villager thanks the player
        conversation["steps"].append({"role": "villager", "action": "speak", "content": random.choice(DICTIONARY_VILLAGER["SELL_COMPLETE"][personality]).replace("{item}", item).replace("{price}", str(sell_price)+' '+CURRENCY)})
    else:
        # Player rejects.
        conversation["steps"].append({"role": "player", "action": "speak", "content": random.choice(DICTIONARY_PLAYER["REJECT_OFFER"])})
        # TODO: counter offer?
        # TODO: Villager responds to rejection?


    conversation["steps"].append({"role": "villager", "action": "speak", "content": generate_goodbye()}) #random.choice(DICTIONARY_VILLAGER["GOODBYES"][personality])})
    conversation["steps"].append({"role": "player", "action": "speak", "content": generate_goodbye()}) #random.choice(DICTIONARY_PLAYER["GOODBYES"])})
    conversation["steps"].append({"role": "player", "action": "leave", "content": ""})

    return conversation



################################################################################################################################



def generate_dataset(size=100000, output_file="minecraft_villager_dataset.json", seed=None, _gzip=True, indent=0, newline=False):
    if seed is None:
        seed = random.randint(0, 99999999)
    random.seed(seed)

    if _gzip:
        if not output_file.endswith(".gz"):
            output_file += ".gz"
    
    #check directory exists
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with (gzip.open(output_file, "wt", encoding="utf-8") if _gzip else open(output_file, "w", encoding="utf-8")) as f:
        # Write the initial structure with no indentation or extra whitespace
        f.write('{ "seed": ' + str(seed) + ', "conversations": [\n')

        # Stream conversations directly to file
        for i in tqdm.tqdm(range(size), desc="Generating and writing conversations", unit="conversation", mininterval=0.25, unit_scale=True):
            conversation = generate_conversation(i)
            # Write each conversation to file immediately after generating it
            # Dont write new lines in json.dump
            json.dump(conversation, f, indent=indent)
            if i < size - 1:
                f.write(',' + ('\n' if newline else ''))  # Add a comma after each conversation except the last one

        # Closing the JSON structure properly
        f.write(']\n}')

    print(f"Dataset saved to {output_file}")

print("-----------------------------------------")
print("Minecraft Villager Convo - Trade Action Generator")
print("Author: Jack (27203747)")
print("Version: 1.0.0")
print("-----------------------------------------")

print("\n--- Generating dataset ---\n")
generate_dataset(size=CONVOS, output_file=OUTPUT_FILE, seed=SEED, _gzip=GZIP, indent=INDENT, newline=NEWLINE)
print("\n--- Dataset generation complete ---\n")