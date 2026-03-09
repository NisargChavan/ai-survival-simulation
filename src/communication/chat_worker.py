import threading
from queue import Queue
from src.llm.ollama_chat import llm
from src.communication.chat import broadcast

chat_queue = Queue()

import threading
from queue import Queue
from src.llm.ollama_chat import llm
from src.communication.chat import broadcast

chat_queue = Queue()


def chat_worker():
    while True:
        task = chat_queue.get()

        if task is None:
            break

        agent, market, recent_chat, step = task

        chat_text = ""

        for msg in recent_chat:
            chat_text += f"{msg['agent']}: {msg['message']}\n"

        prompt = f"""
         You are Agent {agent.name} inside a simulated survival economy.

Your goal is to survive, earn money, and understand the market.

You are speaking in a GLOBAL CHAT visible to all agents.

Speak naturally like a person observing the economy.

--------------------------------
Your personality = {agent.personality}
YOUR CURRENT STATE

Profession: {agent.role}
Energy: {agent.energy}
Money: {agent.money}

Inventory:
Food: {agent.inventory['food']}
Crops: {agent.inventory['crops']}
Wood: {agent.inventory['woods']}
Seeds: {agent.inventory['seeds']}

--------------------------------

MARKET CONDITIONS

Crop Price: {market.prices['crops']}
Wood Price: {market.prices['woods']}


Typical price ranges:
Crops usually trade between 1.0 and 5.0
Wood usually trades between 5.0 and 20.0
--------------------------------

RECENT CHAT
{chat_text}

--------------------------------

RULES
- You may refer to another agent ONLY if they actually spoke in the recent chat.
- Do NOT invent what another agent thinks.
- Do NOT repeat long chains of "A thinks B thinks C".
- Keep the message natural and short (max 15 words).
- Speak like a player discussing the economy.

You may comment on:

• market prices
• resource shortages
• survival concerns
• trade opportunities
• profession choices
• economic speculation
• other agents behavior
• respond to other agents
• disagree with them
• speculate about the market
• discuss resources

--------------------------------

RULES

Write ONE short message (1 sentence).
Speak casually like a player in a strategy game.
Do not explain the simulation.
Do not mention prompts or AI.

Just say what your agent would say.

Example messages:

"Wood prices are getting high, maybe lumberjacks will profit."

"I might need to sell some crops soon."

"Food is getting scarce."

Now write your message.
You MUST respond with a message.
Do not return an empty response.
Do not say nothing.
"""
        

        response = llm.invoke(prompt)

        if response is None:
            response = ""

        response = str(response).strip()

        if response == "":
            response = "The market seems quiet."

        broadcast(agent.name, response, step)

        
        
        with open("chat_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Step {step} | {agent.name}: {response}\n")   


        chat_queue.task_done()


def start_chat_worker():
    thread = threading.Thread(target=chat_worker, daemon=True)
    thread.start()