import random
from colorama import Fore, Style, init
from src.economy.farmer_strategy import FarmerStrategy
from src.economy.lumberjack_strategy import LumberJackStrategy
from src.economy.balanced_strategy import BalancedStrategy

init(autoreset=True)

class Agent:    
    def __init__(self,name,world_width, world_height,danger_weight=1.0, epsilon=0.2):
        self.name = name
        self.world_width = world_width
        self.world_height = world_height
        self.x = random.randint(0, world_width - 1)
        self.y = random.randint(0, world_height - 1)
        self.energy = 25
        self.money = 200
        self.action = ""   
        self.memory = []
        self.visited = []
        self.agent_order_count = {}
        self.farm_memory = []
        self.plot_size = 15
        half = self.plot_size // 2
        self.goal = "maintain"
        self.current_task = None
        self.goal_timer = 0
        if self.name == "A":
         self.wood_target = 30
        elif self.name == "B":
         self.wood_target = 80
        else:
         self.wood_target = 50
        self.plan = []
        self.current_goal_for_plan = None
        self.trade_cooldown = 0
        self.crop_multiplier = 1.0
        self.wood_multiplier = 1.0
        self.role = "generalist"
        self.role_timer = 0

        if self.name == "A":
            # Top-left
            self.plot_center = (half, half)

        elif self.name == "B":
            # Top-right
            self.plot_center = (self.world_width - half - 1, half)

        elif self.name == "C":
            # Bottom-left
            self.plot_center = (half, self.world_height - half - 1)

        else:
            # Default (bottom-right if more agents later)
            self.plot_center = (
                self.world_width - half - 1,
                self.world_height - half - 1
            )
        self.vision = 10
        self.total_food = 0
        self.survival_count = 0 
        self.Panic_mode = None
        self.target = {
            "food": 20,
            "crops": 200,
            "woods": self.wood_target
        }
        self.q_table = {
         i: {"up":0, "down":0, "left":0, "right":0}
         for i in range(50)
         
}
        self.state_names = {
            0:"Safe_NoFood",
            1:"Safe_Food_Up",
            2:"Safe_Food_Down",
            3:"Safe_Food_Left",
            4:"Safe_Food_Right",
            5:"Danger_NoFood",
            6:"Danger_Food_Up",
            7:"Danger_Food_Down",
            8:"Danger_Food_Left",
            9:"Danger_Food_Right"
        }
        self.inventory = {
            "food": 0,
            "seeds": 0,
            "crops" : 0,
            "woods" : 0,
            "normal_farmer_tool" : 0,
            "normal_farmer_tool_durability" : 0,
            "special_farmer_tool" : 0,
            "special_farmer_tool_durability" : 0,
            "rare_crop" : 0
            
        }
        self.danger_weight = danger_weight
        self.epsilon = epsilon
        self.lr = 0.1        
        self.gamma = 0.9    
        
    
    
        
    
    def get_trade_status(self):
     return {
        "needs_wood": self.inventory["woods"] < 20,
        "needs_food": self.inventory["food"] < 5,
        "has_extra_crops": self.inventory["crops"] > 30,
        "has_extra_wood": self.inventory["woods"] > 30
    }
    
    def is_in_plot(self, x, y):
     cx, cy = self.plot_center
     half = self.plot_size // 2
    
     return (
        cx - half <= x <= cx + half and
        cy - half <= y <= cy + half
     )
     
    def decide_market_orders(self, market):
      return self.strategy.decide_orders(market)

 
     
           
    def set_market_strategy(self):

     if self.role == "farmer":
        self.strategy = FarmerStrategy(self)

     elif self.role == "lumberjack":
        self.strategy = LumberJackStrategy(self)

     else:
        self.strategy = BalancedStrategy(self)

    

    def make_plan(self,goal):
        
        self.plan = []
        self.current_goal_for_plan = goal
        
        if goal == "survive":
            self.plan = ["find_food"] * 5
        elif goal == "collect_seeds":
            self.plan =  ["collect_seeds"] * 10
        elif goal == "expand_farm":
         self.plan = [
            "go_to_plot",
            "plant",
            "plant",
            "harvest"
         ] * 3  
         
        elif goal == "build_food_buffer":
            self.plan = ["find_food"] * 10
        
        elif goal == "collect_resource":
            self.plan = ["find_wood"] * 10    
            
        else:  
         self.plan = ["explore"] * 15    
            
   

    def get_next_task(self, goal):

    # If goal changed → new plan
     if goal != self.current_goal_for_plan:
        self.make_plan(goal)

    # If plan finished → remake
     if not self.plan:
        self.make_plan(goal)

     return self.plan.pop(0)
 

    def get_world_summary(self,visible_foods,visible_seeds,ready_crop,visible_woods):
        return{
            "energy" : self.energy,
            "food" : self.inventory['food'],
            "crops" : self.inventory['crops'],
            "seeds" : self.inventory['seeds'],
            "woods" : self.inventory['woods'],
            "farmer_tool" : self.inventory['normal_farmer_tool'],
            'visible_food' : len(visible_foods),
            'visible_seeds' : len(visible_seeds),
            'visible_woods' : len(visible_woods),
            "ready_crop": 1 if ready_crop else 0,
            "in_plot": self.is_in_plot(self.x, self.y)
            
        }
        
        
    def log_state(self, step, goal, task):
     return (
        f"Step {step} | {self.name} | "
        f"G:{goal} | T:{task} | "
        f"Pos:({self.x},{self.y}) | "
        f"E:{self.energy} | "
        f"F:{self.inventory['food']} | "
        f"S:{self.inventory['seeds']} | "
        f"C:{self.inventory['crops']}"
    )    
        
    def decide_goal(self, summary):

     energy = summary["energy"]
     food = summary["food"]
     crops = summary["crops"]
     woods = summary["woods"]
 
    # Absolute survival override
     if energy < 10:
        self.goal = "survive"
        return self.goal, False

     utilities = {}

     if food < 5:
        self.goal = "build_food_buffer"
        return self.goal, False

    # Survival pressure
     utilities["survive"] = max(0, 20 - energy) * 3

    # Food pressure
     utilities["build_food_buffer"] = max(0, 40 - food) * 4

    # -------------------------
    # Farming utility
    # -------------------------
     if self.role == "farmer":
        utilities["expand_farm"] = max(0, 400 - crops) * 3

     elif self.role == "balanced":
        utilities["expand_farm"] = max(0, 400 - crops) * 1.5

     else:
        utilities["expand_farm"] = 0

    # -------------------------
    # Wood utility
    # -------------------------
     if self.role == "lumberjack":
        utilities["collect_resource"] = max(0, 280 - woods) * 3

     elif self.role == "balanced":
        utilities["collect_resource"] = max(0, 280 - woods) * 1.5

     else:
        utilities["collect_resource"] = 0

     utilities["maintain"] = 10

    # Pick highest utility
     self.goal = max(utilities, key=utilities.get)

     return self.goal, False
 
   
    
    def task_to_action(self,task,target):
        
        if task in ["find_food", "collect_seeds", "harvest", "go_to_plot" , "find_wood"]:
         if target:
            return self.direction_to_target(target)
         else:
            return random.choice(["up","down","left","right"])

        
        if task == "plant":
            return random.choice(["up","down","left","right"])  
        
        elif task == "explore":
            state = self.get_state([], [])
            return random.choice(["up","down","left","right"]) 
    
    
    def get_ready_crop(self, crops):
     for pos in self.farm_memory:
        if pos in crops:
            if crops[pos] == self.name:
                return pos
     return None

    def get_plot_target(self):
     return self.plot_center
       
    def in_danger(self, dangers):
        return (self.x, self.y) in dangers   
    
    #   [UNUSED]
    def get_ready_food(self,farms):
        for fx , fy in self.farm_memory:
            if (fx,fy) in farms:
                farm = farms[(fx, fy)]
                
                if farm["owner"] == self.name and farm["timer"] <= 2:
                    return (fx, fy)
                
        return None    
    #   [UNUSED]
    def danger_nearby_direction(self,dangers):
        if not dangers:
            return None
        
        nearest = None
        min_distance = 999
        
        for dx , dy in dangers:
             dist = abs(self.x - dx) + abs(self.y - dy)
             if dist < min_distance:
                 min_distance = dist
                 nearest = (dx , dy)
        
        if min_distance > 2:
             return None
              
              
        dx = nearest[0] - self.x
        dy = nearest[1] - self.y

        if abs(dx) > abs(dy):
                return "right" if dx > 0 else "left"
        else:
                return "up" if dy > 0 else "down" 
        
        
        
    def get_direction(self,visible_foods):
        if not visible_foods:
            return None
        
        fx,fy = min(
            visible_foods,
            key = lambda f : abs(self.x- f[0]) + abs(self.y - f[1])
        )
        
        dx = fx - self.x
        dy = fy - self.y
       
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "up" if dy > 0 else "down"
      
      
    def is_danger_nearby(self,dangers):
        for dx , dy in dangers:
            distance = abs(self.x - dx) + abs(self.y-dy)
            if distance <= 1:
                return True
        return False    
              
       
 #   [UNUSED]        
    def get_nearest_memory_food(self):
        if not self.memory:
           return None
            
        Nearest = None
        min_dist = 999
        
        for fx , fy , age  in self.memory:
            if age > 6:
               continue
            
            dist = abs(self.x-fx) + abs(self.y-fy)
            if dist < min_dist:
                min_dist = dist
                Nearest = (fx , fy)
                
        return Nearest 
    
    
    def avoid_danger(self, action, dangers):
     nx, ny = self.x, self.y
    
     if action == "up":
        ny += 1
     elif action == "down":
        ny -= 1
     elif action == "left":
        nx -= 1
     elif action == "right":
        nx += 1
    
     if (nx, ny) in dangers:
        return random.choice(["up","down","left","right"])
    
     return action       
            
               
    def direction_to_target(self,target):
        tx , ty = target
        dx = tx - self.x   
        dy = ty - self.y
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
           return "up" if dy > 0 else "down"
       
        
        
    def get_state(self, visible_foods, dangers):

    # -------------------------
    # 1. Energy Level (2)
    # -------------------------
     if self.energy > 10:
        energy_index = 0   # High energy
     else:
        energy_index = 1   # Low energy

    # -------------------------
    # 2. Food Direction (5)
    # -------------------------
     food_dir = self.get_direction(visible_foods)

     food_map = {
        None: 0,
        "up": 1,
        "down": 2,
        "left": 3,
        "right": 4
     }

     food_index = food_map[food_dir]

    # -------------------------
    # 3. Danger Nearby (2)
    # -------------------------
     danger_near = 1 if self.is_danger_nearby(dangers) else 0

    # -------------------------
    # Final State (0–19)
    # Formula:
    # energy (0/1) * 10
    # + food (0–4) * 2
    # + danger (0/1)
    # -------------------------
     state = energy_index * 10 + food_index * 2 + danger_near
     return state
        
    def learn(self,state,action,reward,next_state):
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())    
        
        #formula
        new_value = old_value + self.lr * (
        reward + self.gamma * next_max - old_value
        )
        
        self.q_table[state][action] = new_value
    #    
    
    
    
        
        
        
    def choose_action(self,state):
        actions = ["up", "down", "left", "right"]
        
        
        if random.random() < self.epsilon:
            action = random.choice(actions)
           # print(Fore.BLUE + f"{self.name} exploring (RL) → {action}")
            return action
        
        action = max(self.q_table[state],key= self.q_table[state].get)
      #  print(Fore.GREEN + f"{self.name} exploiting (RL) → {action}")
        return action

    
        
    def update_mode(self):
      if self.energy < 10:
          self.mode = "Panic"
          print(Fore.RED + f"{self.name} is panicing!!")
      else:
          self.mode = None         
        
    def get_visible_food(self,foods):
        visible = []
        for fx ,fy in foods:
            distance = abs(fx-self.x) + abs(fy-self.y)
            if distance <= self.vision:
                visible.append((fx,fy))
        return visible    
        
        
    def update_memory(self,foods): 
             for food in foods:
                 if food not in [( fx ,fy) for fx , fy, _ in self.memory]:
                      self.memory.append((food[0],food[1],0))
        
             new_memory = []
             
             for fx , fy , age in self.memory:
                 age +=1
                 if age < 10:
                  new_memory.append((fx,fy,age))
                  
                  
             self.memory = new_memory
        
        
    def update_visited(self):
        
        if(self.x , self.y) not in [(vx,vy) for vx,vy, _ in self.visited  ]:
            self.visited.append((self.x , self.y , 0))
            
        new_visited = [] 
        
        for vx , vy , age in self.visited:
            age +=1
            if age < 20:
                new_visited.append((vx,vy,age))
        
        
        self.visited = new_visited
        
        
    def move(self, direction):
     old_x, old_y = self.x, self.y
     new_x, new_y = self.x, self.y
   
    # Move
     if direction == "up":
        self.y += 1
     elif direction == "down":
        self.y -= 1    
     elif direction == "left":
        self.x -= 1    
     elif direction == "right":
        self.x += 1 

    # Clamp to grid
     self.x = max(0, min(self.world_width - 1, self.x))
     self.y = max(0, min(self.world_height - 1, self.y))

    # # obstacle check
    #  if (new_x, new_y) not in obstacles:
    #     self.x, self.y = new_x, new_y
    #  else:
    #     # hit obstacle
    #     self.energy -= 1

    # Check if position didn't change → hit wall
     hit_wall = (self.x == old_x and self.y == old_y)



    # Energy cost
     self.energy -=1    
     

     if self.energy == 0:
        print(Fore.LIGHTRED_EX + f"{self.name} died lmao")

     self.action = direction

     return hit_wall

                
    def status(self):
        return f"name : {self.name}  Postion | {self.x} , {self.y} Energy ,{self.energy} direction : {self.action}"  
    