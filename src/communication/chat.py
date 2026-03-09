
global_chat = []

def broadcast(agent_name, message, step):
    global_chat.append({
        "step": step,
        "agent": agent_name,
        "message": message
    })

def get_recent_chat(limit=5):
    return global_chat[-limit:]