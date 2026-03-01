import random
from colorama import Fore, Style, init

init(autoreset=True)

class Agent:    
    def __init__(self,name,world_width, world_height,danger_weight=1.0, epsilon=0.2):
        self.name = name
        self.world_width = world_width
        self.world_height = world_height
        self.x = random.randint(0, world_width - 1)
        self.y = random.randint(0, world_height - 1)
        self.energy = 25
        self.action = ""   
        self.memory = []
        self.visited = []
        self.farm_memory = []
        self.plot_size = 15
        self.plot_size = 15
        self.plot_size = 15
        half = self.plot_size // 2
        self.goal = "maintain"
        self.current_task = None
        self.goal_timer = 0

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
            "crops" : 0
        }
        self.danger_weight = danger_weight
        self.epsilon = epsilon
        self.lr = 0.1        
        self.gamma = 0.9    
        
    
    
    def is_in_plot(self, x, y):
     cx, cy = self.plot_center
     half = self.plot_size // 2
    
     return (
        cx - half <= x <= cx + half and
        cy - half <= y <= cy + half
     )


    def get_world_summary(self,visible_foods,visible_seeds,ready_crop):
        return{
            "energy" : self.energy,
            "food" : self.inventory['food'],
            "crops" : self.inventory['crops'],
            "seeds" : self.inventory['seeds'],
            'visible_food' : len(visible_foods),
            'visible_seeds' : len(visible_seeds),
            "ready_crop": 1 if ready_crop else 0,
            "in_plot": self.is_in_plot(self.x, self.y)
            
        }
        
        
    def decide_goal(self, summary):
    # keep current goal for some time
     if self.goal_timer > 0:
        self.goal_timer -= 1
        return self.goal

     energy = summary["energy"]
     seeds = summary["seeds"]
     crops = summary["crops"]
     food = summary["food"]

     if energy < 15:
        self.goal = "survive"
        self.goal_timer = 5

     elif seeds < 3:
        self.goal = "collect_seeds"
        self.goal_timer = 10

     elif crops < 200:
        self.goal = "expand_farm"
        self.goal_timer = 20

     elif food < 10:
        self.goal = "build_food_buffer"
        self.goal_timer = 10

     else:
        self.goal = "maintain"
        self.goal_timer = 15

     return self.goal    
 
 
    
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
        print(Fore.LIGHTCYAN_EX + f"{dx} , {dy}")
        
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
        print(
    Fore.MAGENTA +
    f"{self.name} Q Update | S:{state} A:{action} → {round(new_value,2)}"
       )
        
        
        
    def choose_action(self,state):
        actions = ["up", "down", "left", "right"]
        
        
        if random.random() < self.epsilon:
            action = random.choice(actions)
            print(Fore.BLUE + f"{self.name} exploring (RL) → {action}")
            return action
        
        action = max(self.q_table[state],key= self.q_table[state].get)
        print(Fore.GREEN + f"{self.name} exploiting (RL) → {action}")
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

     if hit_wall:
        print(Fore.LIGHTRED_EX + f"{self.name} hit wall!")

    # Energy cost
     self.energy -=1    
     

     if self.energy == 0:
        print(Fore.LIGHTRED_EX + f"{self.name} died lmao")

     self.action = direction

     return hit_wall

                
    def status(self):
        return f"name : {self.name}  Postion | {self.x} , {self.y} Energy ,{self.energy} direction : {self.action}"  
    