
import random
from src.agent import Agent
from colorama import Fore, init
import datetime
from ui.visual import draw_world
import pygame
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="darkgrid")
init(autoreset=True)

# ===============================
# CONFIG
# ===============================
WORLD_WIDTH = 40
WORLD_HEIGHT = 40
EPISODES = 300
STEPS_PER_EPISODE = 10000

# ===============================
# LOG SETUP
# ===============================
LOG_FILE = "run_log.txt"
log_buffer = []

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
    Agent("C", WORLD_WIDTH, WORLD_HEIGHT, danger_weight=0.7, epsilon=0.25)
]

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

    log(f"\n===== EPISODE {episode+1} =====")

    episode_reward = 0
    episode_food_eaten = 0
    episode_seeds_collected = 0

    # Reset world
    foods = []
    seeds = []
    dangers = []
    farms = {}
    crops = {}

    # Danger zones
    for _ in range(5):
        dangers.append((
            random.randint(0, WORLD_WIDTH-1),
            random.randint(0, WORLD_HEIGHT-1)
        ))

    # Reset agents
    for agent in agents:
        # Spawn near agent's plot (fair start)
        px, py = agent.get_plot_target()
        agent.x = min(WORLD_WIDTH-1, max(0, px + random.randint(-3, 3)))
        agent.y = min(WORLD_HEIGHT-1, max(0, py + random.randint(-3, 3)))
        agent.energy = 25
        agent.memory = []
        agent.inventory['seeds'] = 0
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
             fx = random.randint(0,WORLD_WIDTH-1)
             fy = random.randint(0,WORLD_HEIGHT-1)
             if not len(foods) > 50:
              foods.append((fx,fy))
              
              
             

        for agent in agents:
         if random.random() < 0.09:
            sx = min(WORLD_WIDTH-1, max(0, agent.x + random.randint(-5,5)))
            sy = min(WORLD_HEIGHT-1, max(0, agent.y + random.randint(-5,5)))
            seeds.append((sx, sy))

        # Farm growth
        for pos in list(farms.keys()):
            farms[pos]["timer"] -= 1
            if farms[pos]["timer"] <= 0:
                crops[pos] = farms[pos]["owner"]
                del farms[pos]

        # Quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # ===============================
        # AGENT LOOP
        # ===============================
        for agent in agents:

            if agent.energy <= 0:
                continue
            
            if agent.energy < 10 and agent.inventory['food'] > 0:
                agent.inventory['food'] -= 1
                agent.energy += 10
                log(f"{agent.name} ate from inventory")
            
            visible_foods = agent.get_visible_food(foods)
            visible_seeds = agent.get_visible_food(seeds)

            state = None
            Used_Rl = False

            # =====================================================
            # PRIORITY 1: SURVIVAL
            # =====================================================
            if agent.energy < 10:

                 # 1) Visible food
                if visible_foods:
                    target = min(
                        visible_foods,
                        key=lambda f: abs(agent.x-f[0]) + abs(agent.y-f[1])
                    )
                    action = agent.direction_to_target(target)

                # 2) Own ready crop
                elif agent.get_ready_crop(crops):
                    target = agent.get_ready_crop(crops)
                    action = agent.direction_to_target(target)
                    log(f"{agent.name} PANIC → crop")

                # 3) Inventory fallback
                elif agent.inventory['food'] > 0:
                    agent.inventory['food'] -= 1
                    agent.energy += 10
                    continue

                # 4) Last resort
                else:
                    action = random.choice(["up","down","left","right"])

                action = agent.avoid_danger(action, dangers)

            # =====================================================
            # PRIORITY 2: HARVEST READY CROPS
            # =====================================================    
            elif agent.get_ready_crop(crops):
                target = agent.get_ready_crop(crops)
                action = agent.direction_to_target(target)
                action = agent.avoid_danger(action, dangers)
                log(f"{agent.name} going to harvest")
    
            # =====================================================
            # PRIORITY 3: COLLECT SEEDS
            # =====================================================
            elif visible_seeds and agent.inventory['seeds'] < 5:

                target = min(
                    visible_seeds,
                    key=lambda s: abs(agent.x-s[0]) + abs(agent.y-s[1])
                )
                action = agent.direction_to_target(target)
                action = agent.avoid_danger(action, dangers)
                
            
            # =====================================================
            # PRIORITY 4: GO TO PLOT
            # =====================================================
            elif agent.inventory['seeds'] > 4:

                if not agent.is_in_plot(agent.x, agent.y):
                    target = agent.get_plot_target()
                    action = agent.direction_to_target(target)
                else:
                    action = random.choice(["up","down","left","right"])

                action = agent.avoid_danger(action, dangers)

            # =====================================================
            # PRIORITY 5: NORMAL RL FOOD
            # =====================================================
            elif visible_foods:

                state = agent.get_state(visible_foods, dangers)
                action = agent.choose_action(state)
                action = agent.avoid_danger(action, dangers)
                Used_Rl = True

            # =====================================================
            # PRIORITY 6: EXPLORE
            # =====================================================
            else:
                action = random.choice(["up","down","left","right"])
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

            # Plant
            if (
                agent.inventory['seeds'] > 0
                and agent.is_in_plot(agent.x, agent.y)
                and pos not in farms
                and pos not in dangers
            ):
                farms[pos] = {"timer":30, "owner":agent.name}
                agent.inventory['seeds'] -= 1
                agent.farm_memory.append(pos)
                reward += 2

            # Eat food
            if pos in foods:
                foods.remove(pos)
                agent.inventory['food'] += 1
                agent.energy += 10
                reward += 25
                episode_food_eaten += 1

            # Harvest
            if pos in crops and crops[pos] == agent.name:
                del crops[pos]
                agent.inventory['food'] += 1
                agent.energy += 10
                reward += 25
                episode_food_eaten += 1
                
            if pos in agent.farm_memory:
             agent.farm_memory.remove(pos)    

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

        # Draw world
        draw_world(agents, foods, farms, crops, episode+1, step+1, [], dangers)

    # Episode stats
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

