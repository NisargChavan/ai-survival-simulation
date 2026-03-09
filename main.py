
import random
from src.agent import Agent
from colorama import Fore, init
import datetime
from ui.visual import draw_world
import pygame
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.market import Market
from src.market import market
from src.communication.chat import broadcast, get_recent_chat
from src.communication.chat_worker import chat_queue
# from src.communication.chat_worker import start_chat_worker

# start_chat_worker()


CHAT_INTERVAL = 100
TEST_INTERVAL = 1000
MARKET_INTERVAL = 50
ORDER_SUBMISSION_INTERVAL = 3

sns.set(style="darkgrid")
init(autoreset=True)
zoom = 1

def attempt_trade(a, b):

    if a.trade_cooldown > 0 or b.trade_cooldown > 0:
        return

    status_a = a.get_trade_status()
    status_b = b.get_trade_status()
    


    trade_amount = 5

    # Case 1: A needs wood, B has wood, A has crops
    if (
        status_a["has_extra_crops"]
        and status_a["needs_wood"]
        and status_b["has_extra_wood"]
    ):
        a.inventory["crops"] -= trade_amount
        b.inventory["crops"] += trade_amount

        b.inventory["woods"] -= trade_amount
        a.inventory["woods"] += trade_amount

        a.trade_cooldown = 10
        b.trade_cooldown = 10

        log(f"TRADE: {a.name} → {b.name} (crops for wood)")

    # Case 2: reverse
    elif (
        status_b["has_extra_crops"]
        and status_b["needs_wood"]
        and status_a["has_extra_wood"]
    ):
        b.inventory["crops"] -= trade_amount
        a.inventory["crops"] += trade_amount

        a.inventory["woods"] -= trade_amount
        b.inventory["woods"] += trade_amount

        a.trade_cooldown = 10
        b.trade_cooldown = 10

        log(f"TRADE: {b.name} → {a.name} (crops for wood)")




# ===============================
# CONFIG
# ===============================
WORLD_WIDTH = 60
WORLD_HEIGHT = 60
EPISODES = 300
STEPS_PER_EPISODE = 10000

# ===============================
# LOG SETUP
# ===============================
LOG_FILE = "run_log.txt"
MARKET_LOG_FILE = "market_log.txt"
log_buffer = []
CHAT_LOG_FILE = "chat_log.txt"

with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
    f.write("AI Survival World - Global Chat Log\n")
    f.write("====================================\n\n")


with open(MARKET_LOG_FILE, "w") as f:
    f.write("AI Survival World - Market Log\n")
    f.write("====================================\n\n")


with open(LOG_FILE, "w") as f:
    f.write("AI Survival World Run Log\n")
    f.write(f"Run Time: {datetime.datetime.now()}\n")
    f.write("====================================\n")

def log(text):
    log_buffer.append(text)

# ===============================
# CREATE AGENTS
# ===============================
agents = [
    Agent("A", WORLD_WIDTH, WORLD_HEIGHT, danger_weight=1.5, epsilon=0.25),
    Agent("B", WORLD_WIDTH, WORLD_HEIGHT, danger_weight=1.0, epsilon=0.25),
    Agent("C", WORLD_WIDTH, WORLD_HEIGHT, danger_weight=0.7, epsilon=0.25),
    Agent("D", WORLD_WIDTH, WORLD_HEIGHT, danger_weight=1.0, epsilon=0.25),
]

def count_professions(agents):

    counts = {
        "farmer": 0,
        "lumberjack": 0,
        "balanced": 0
    }

    for a in agents:
        counts[a.role] += 1

    return counts


print(Fore.GREEN + "Simulation started...")

# ===============================
# METRICS
# ===============================
episode_rewards = []
episode_foods = []
episode_avg_energy = []
episode_seeds = []

# ===============================
# EPISODES
# ===============================
for episode in range(EPISODES):
    
    log_buffer.clear() 
    
    
    # Bootstrap market
    for _ in range(5):
     market.sell_orders.setdefault("crops", []).append({
        "agent": agents[0],  
        "qty": 200,
        "age": 0
    })

    for _ in range(5):
     market.sell_orders.setdefault("woods", []).append({
        "agent": agents[1],
        "qty": 20,
        "age": 0
    })

    log(f"\n===== EPISODE {episode+1} =====")

    episode_reward = 0
    episode_food_eaten = 0
    episode_seeds_collected = 0
    episode_woods_collected = 0
    episode_normal_tool_crafted = 0
    episode_speical_tool_crafted = 0
    
    

    # Reset world
    foods = []
    seeds = []
    woods = []
    dangers = []
    farms = {}
    crops = {}
    
    agents[0].role = "farmer"
    agents[1].role = "lumberjack"
    agents[2].role = "balanced"
    agents[3].role = "farmer"
    
    
    
    
    for agent in agents:
        agent.set_market_strategy()
    
    for agent in agents:

        print(agent.role)
        
            
        log(f"{agent.name} starts as {agent.role}")
        print(f"{agent.name} starts as {agent.role}")

    # Danger zones
    for _ in range(5):
        dangers.append((
            random.randint(0, WORLD_WIDTH-1),
            random.randint(0, WORLD_HEIGHT-1)
        ))

    # Reset agents
    for agent in agents:
        px, py = agent.get_plot_target()
        agent.x = min(WORLD_WIDTH-1, max(0, px + random.randint(-3, 3)))
        agent.y = min(WORLD_HEIGHT-1, max(0, py + random.randint(-3, 3)))
        agent.energy = 25
        agent.money = 25
        agent.memory = []
        agent.inventory['seeds'] = 5
        agent.inventory['food'] = 40
        agent.inventory['woods'] = 0
        agent.inventory['special_farmer_tool'] = 0
        agent.inventory['normal_farmer_tool'] = 0
        agent.tool_durability['normal_farmer_tool_durability'] = 0
        agent.tool_durability['special_farmer_tool_durability'] = 0
        agent.inventory['rare_crop'] = 0
    
        
        
        agent.epsilon = max(0.05, agent.epsilon * 0.995)

    # ===============================
    # STEPS
    # ===============================
    for step in range(STEPS_PER_EPISODE):
        
       
        
       
        
        if all(agent.energy <= 0 for agent in agents):
            print(f"Episode {episode+1}: All agents died at step {step}")
            log(f"All agents died at step {step}")
            break

        # Spawn resources
        if random.random() < 0.7:
            fx = random.randint(0, WORLD_WIDTH-1)
            fy = random.randint(0, WORLD_HEIGHT-1)
            
            if fy >= 44:
             continue

           # Check if inside any agent plot
            in_any_plot = False
            for ag in agents:
                if ag.is_in_plot(fx, fy):
                    in_any_plot = True
                    break

            # Spawn only if not inside plot and limit not exceeded
            if not in_any_plot and len(foods) < 50:
                foods.append((fx, fy))
        
        if random.random() < 0.7:

            fx = random.randint(0, WORLD_WIDTH - 1)
            fy = random.randint(0, WORLD_HEIGHT - 1)
            
            
            if fy >= 44:
             continue

            
            BUFFER = 3
            MIN_TREE_DISTANCE = 3

            in_any_plot = False

            # --- Check farm buffer ---
            for ag in agents:

                cx, cy = ag.plot_center
                half_w = ag.plot_width // 2
                half_h = ag.plot_height // 2

                left   = cx - half_w - BUFFER
                right  = cx + half_w + BUFFER
                top    = cy - half_h - BUFFER
                bottom = cy + half_h + BUFFER

                if left <= fx <= right and top <= fy <= bottom:
                    in_any_plot = True
                    break

            # --- Check tree spacing ---
            too_close = False
            for wx, wy in woods:
                if abs(wx - fx) <= MIN_TREE_DISTANCE and abs(wy - fy) <= MIN_TREE_DISTANCE:
                    too_close = True
                    break

            # --- Spawn tree ---
            if not in_any_plot and not too_close and len(woods) < 70:
                woods.append((fx, fy))
        
        # if step % CHAT_INTERVAL == 0:

        #     speaker = random.choice(agents)

        #     recent_chat = get_recent_chat()
             
        #     for agent in agents:
        #        chat_queue.put((agent, market, recent_chat, step))

        if step % TEST_INTERVAL == 0:
            for agent in agents:
                print(Fore.RED+f"{agent.name} : {agent.mo}")        
                
                
        #Market   
        if step % ORDER_SUBMISSION_INTERVAL == 0:
         for agent in agents:
          if agent.energy <= 0:
              continue

          orders = agent.decide_market_orders(market) or []

          for order_type, item, qty in orders:
           if order_type == "sell":
            market.sumbit_sell_order(agent, item, qty)
           else:
            market.sumbit_buy_order(agent, item, qty)



        if step % MARKET_INTERVAL == 0:

          market.current_step = step

    
          market.clear_market()
 
          random.shuffle(agents)

          for agent in agents:
            profession_counts = count_professions(agents)

            agent.evaluat_economy(profession_counts)

          print(
            f"[Market] Step {step} | "
            f"Crops: {market.prices['crops']:.2f} | "
            f"Woods: {market.prices['woods']:.2f} | "
            f"Normal Farmer Tool : {market.prices['normal_farmer_tool']:.2f} | "
            f"Special Farmer Tool : {market.prices['special_farmer_tool']:.2f} | "
            f"Rare Crops: {market.prices['rare_crop']:.2f} | "
          )

                
             

        for agent in agents:
         if random.random() < 0.7:
            sx = min(WORLD_WIDTH-1, max(0, agent.x + random.randint(-8,8)))
            sy = min(WORLD_HEIGHT-1, max(0, agent.y + random.randint(-8,8)))
        
            seeds.append((sx,sy))


        # Farm growth
        for pos in list(farms.keys()):
            farms[pos]["timer"] -= 1
            if farms[pos]["timer"] <= 0:
                crops[pos] = farms[pos]["owner"]
                del farms[pos]


        
                
        # Quit event
    
        for event in pygame.event.get():
           
        
         if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                zoom += 0.1
            elif event.y < 0:
                zoom -= 0.1
            zoom = max(0.5, min(zoom, 2.5))
         if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                

        # ===============================
        # AGENT LOOP
        # ===============================
        for agent in agents:

            if agent.trade_cooldown > 0:
              agent.trade_cooldown -= 1


            if agent.energy <= 0:
                continue
            
            if agent.energy < 10:
                
             if agent.inventory['food'] > 0:
                agent.inventory['food'] -= 1
                agent.energy += 10
              

             elif agent.inventory.get('crops', 0) > 0:
                agent.inventory['crops'] -= 1
                agent.energy += 7
                
             
            # Auto craft tool if none 
            if agent.role == "lumberjack" and  agent.inventory["special_farmer_tool"] == 0  and agent.inventory["woods"] >= 150 and agent.inventory["rare_crop"] >= 2:
                agent.inventory["woods"] -= 150
                agent.inventory["rare_crop"] -= 2
                agent.inventory["special_farmer_tool"] += 1
                episode_speical_tool_crafted +=1
                log(f"{agent.name} crafted a special farming tool at {step} step!!")
                agent.tool_durability["special_farmer_tool"] = 100      
                
                
            if  agent.role == "lumberjack" and agent.inventory["normal_farmer_tool"] == 0 and agent.inventory["woods"] >=50:
                agent.inventory["woods"] -= 50
                agent.inventory["normal_farmer_tool"] += 1
                episode_normal_tool_crafted += 1
                agent.tool_durability["normal_farmer_tool_durability"] = 60 
                
            if agent.inventory["crops"] > 300 and agent.role == "farmer":
                agent.inventory['crops'] -= 200
                agent.inventory['rare_crop']  += 1  
                
                 
        
                 
            
            visible_foods = agent.get_visible_food(foods)
            visible_seeds = agent.get_visible_food(seeds)
            visible_woods = agent.get_visible_food(woods)
            
            ready_crop = agent.get_ready_crop(crops)
            
            # Wealth-aware behavior
            if agent.inventory['crops'] > 500:
                ready_crop = None   # stop harvesting for a while

            # FOOD BUFFER LOGIC
            # ===============================
            # If agent already has enough food, ignore random food
            if agent.inventory['food'] >= 20:
                visible_foods = []
                
                
            state = None
            Used_Rl = False
           
            summary = agent.get_world_summary(visible_foods,visible_seeds,ready_crop,visible_woods)
            goal , goal_changed = agent.decide_goal(summary)             
            task = agent.get_next_task(goal)
            
            target = None

            if task == "find_food" and visible_foods:
                target = min(
                    visible_foods,
                    key=lambda f: abs(agent.x-f[0]) + abs(agent.y-f[1])
                )
            elif task == "collect_seeds" and visible_seeds:
                target = min(
                    visible_seeds,
                    key=lambda s: abs(agent.x-s[0]) + abs(agent.y-s[1])
                )
            elif task == "harvest":
                target = ready_crop

            elif task == "go_to_plot":
                target = agent.get_plot_target()
                
            elif task == "find_wood" and visible_woods:
                target = min(
                    visible_woods,
                    key=lambda f: abs(agent.x-f[0]) + abs(agent.y-f[1])
                )
                    
                
                      
            if task in ["explore", "find_food", "find_wood", "collect_seeds"] and target is None:
                state = agent.get_state(visible_foods, dangers)
                action = agent.choose_action(state)
                Used_Rl = True
            else:
                action = agent.task_to_action(task, target)

            action = agent.avoid_danger(action, dangers)
            
            # ===============================
            # MOVE
            # ===============================
            reward = -1
            hit_wall = agent.move(action)
            

            pos = (agent.x, agent.y)

            # Collect seed
            if pos in seeds:
                seeds.remove(pos)
                agent.inventory['seeds'] += 1
                episode_seeds_collected += 1
                reward += 1

            if pos in woods:
                woods.remove(pos)
                agent.is_chopping = True
                agent.axe_frame = 0
                wood_gain = int(1 * agent.wood_multiplier)
                wood_gain = max(1, wood_gain)
                agent.inventory['woods'] += wood_gain
                episode_woods_collected +=1
                reward +=1
                
            
            # Plant
            if (
                agent.role == "farmer" and
                agent.inventory['seeds'] > 0
                and agent.is_in_plot(agent.x, agent.y)
                and pos not in farms
                and pos not in dangers
            ):
                farms[pos] = {"timer":15, "owner":agent.name}
                agent.inventory['seeds'] -= 1
                agent.farm_memory.append(pos)
                
                agent.is_farming = True
                agent.hoe_frame = 0
                
                reward += 2

            # Eat food
            if pos in foods:
                foods.remove(pos)
                agent.inventory['food'] += 1
                agent.energy += 10
                reward += 25
                episode_food_eaten += 1

           # Harvest
            if agent.role == "farmer" and pos in crops and crops[pos] == agent.name:
                del crops[pos]
                
                energy_gain = 9
                crop_gain = int(1 * agent.crop_multiplier)
                
                
                            
                if agent.inventory.get("special_farmer_tool" , 0) > 0:
                     crop_gain =  int(2 * agent.crop_multiplier)
                     energy_gain = 10
                     agent.tool_durability["special_farmer_tool_durability"] -= 1
                    
                     if random.random() < 0.05:
                        agent.inventory["rare_crop"] += 1
                        
                     
                     if agent.tool_durability["special_farmer_tool_durability"] <= 0:
                         agent.inventory["special_farmer_tool"] = 0  
                     
                
                
                elif agent.inventory.get("normal_farmer_tool", 0) > 0:
                     crop_gain =  int(1 * agent.crop_multiplier)
                     energy_gain = 8
                     agent.tool_durability["normal_farmer_tool_durability"] -= 1
                     
                     if agent.tool_durability["normal_farmer_tool_durability"] <= 0:
                         agent.inventory["normal_farmer_tool"] = 0
                     
                                                     
                agent.energy += energy_gain
                agent.energy = min(agent.energy, 100)
                
                reward += 25
                agent.inventory['crops'] +=crop_gain
            
                episode_food_eaten += 1
                
                
            if agent.inventory['crops'] >= 2 and agent.inventory['food'] < 10:
                    agent.inventory['crops'] -= 2
                    agent.inventory['food'] += 2

            

            # Danger
            if pos in dangers:
                agent.energy -= 6
                reward -= int(20 * agent.danger_weight)

            # Learn
            episode_reward += reward
            if Used_Rl:
                next_visible = agent.get_visible_food(foods)
                next_state = agent.get_state(next_visible, dangers)
                agent.learn(state, action, reward, next_state)
                
                
            # ===============================
# TRADING PHASE 
# ===============================
        for i in range(len(agents)):
                for j in range(i + 1, len(agents)):
                    a = agents[i]
                    b = agents[j]
                   
                    if a.energy <= 0 or b.energy <= 0:
                        continue

                    distance = abs(a.x - b.x) + abs(a.y - b.y)

                    if distance <= 4:
                        attempt_trade(a, b)    

        # Draw world
        draw_world(agents, foods, farms, crops,woods ,episode+1, step+1, [], dangers , visible_seeds,zoom,action)
        
    if market.episode_history:
         with open("market_log.txt", "a" , encoding="utf-8") as f:
            f.write(f"\n===== EPISODE {episode+1} TRADE HISTORY =====\n")

            for trade in market.episode_history:
                f.write(
                f"Step {trade['step']} | "
                f"{trade['seller']} → {trade['buyer']} | "
                f"{trade['item']} x{trade['quantity']} "
                f"@ {trade['price']}\n"
            )

            f.write("=============================================\n")

    # Episode stats
    for agent in agents:
     log(f"{agent.name} Role: {agent.role}")
     log(f"{agent.name} Money : {agent.money} | Food: {agent.inventory['food']} | Seeds: {agent.inventory['seeds']} | Crops: {agent.inventory['crops']} | Woods: {agent.inventory['woods']} | Normal Farmer Tool: {agent.inventory['normal_farmer_tool']} | Special Farmer Tool: {agent.inventory['special_farmer_tool']} | Rare Crop : {agent.inventory['rare_crop']} |Normal tool : {episode_normal_tool_crafted}|Special tool : {episode_speical_tool_crafted}| Seeds collected : {episode_seeds_collected} |Energy: {agent.energy}")

    alive = [a for a in agents if a.energy > 0]
    avg_energy = sum(a.energy for a in alive)/len(alive) if alive else 0

    episode_rewards.append(episode_reward)
    episode_foods.append(episode_food_eaten)
    episode_avg_energy.append(avg_energy)
    episode_seeds.append(episode_seeds_collected)
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
     for line in log_buffer:
        f.write(line + "\n")

log_buffer.clear()
# ===============================
# RESULTS
# ===============================
for a in agents:
    log(f"{a.name} inv : {a.inventory}")


print(Fore.GREEN + "Simulation finished")

episodes = list(range(1, EPISODES+1))
data = pd.DataFrame({
    "Episode": episodes,
    "Reward": episode_rewards,
    "Food": episode_foods,
    "Energy": episode_avg_energy,
    "Seeds": episode_seeds
})

plt.figure(figsize=(10,6))
sns.lineplot(data=data, x="Episode", y="Food")
sns.lineplot(data=data, x="Episode", y="Seeds")
plt.title("Food vs Seeds")
plt.show()

