import pygame
import os

# ===============================
# WORLD SETTINGS
# ===============================
WORLD_WIDTH = 60
WORLD_HEIGHT = 60

# Maximum window size (to keep it reasonable)
MAX_SCREEN_WIDTH = 1000
MAX_SCREEN_HEIGHT = 800

# ===============================
# AUTO CELL SIZE (Fit to screen)
# ===============================
CELL_SIZE_X = MAX_SCREEN_WIDTH // WORLD_WIDTH
CELL_SIZE_Y = MAX_SCREEN_HEIGHT // WORLD_HEIGHT
CELL_SIZE = min(CELL_SIZE_X, CELL_SIZE_Y)



SCREEN_WIDTH = WORLD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = WORLD_HEIGHT * CELL_SIZE

world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

AGENT_SCALE = int(CELL_SIZE * 4)
WOOD_SCALE = int(CELL_SIZE * 1.3)
CROP_SCALE = int(CELL_SIZE * 1)

# ===============================
# INIT
# ===============================
pygame.init()
pygame.font.init()
zoom = 1
zoom = max(1.0, min(zoom, 3.0))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Survival World")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 18)

# ===============================
# ASSETS
# ===============================
ASSET_PATH = os.path.join("assets")

grass_img = pygame.image.load(os.path.join(ASSET_PATH, "grass.png"))
grass_img = pygame.transform.scale(grass_img, (CELL_SIZE, CELL_SIZE))

seed_img = pygame.image.load(os.path.join(ASSET_PATH, "seeds.png"))
seed_img = pygame.transform.scale(seed_img, (CROP_SCALE, CROP_SCALE))

visible_Seeds_img = pygame.image.load(os.path.join(ASSET_PATH ,  "visible_seeds.png"))
visible_Seeds_img = pygame.transform.scale(visible_Seeds_img ,(CELL_SIZE , CELL_SIZE))

ground_img = pygame.image.load(os.path.join(ASSET_PATH, "ground_2.png")).convert()

ground_img = pygame.transform.scale(
    ground_img,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)


wood_img = pygame.image.load(os.path.join(ASSET_PATH, "woods.png"))
wood_img = pygame.transform.scale(wood_img, (WOOD_SCALE,  WOOD_SCALE))

crop_img = pygame.image.load(os.path.join(ASSET_PATH, "crop.png"))
crop_img = pygame.transform.scale(crop_img, (CROP_SCALE, CROP_SCALE))

farmland_img = pygame.image.load(os.path.join(ASSET_PATH, "farmland.png"))
farmland_img = pygame.transform.scale(farmland_img, (CELL_SIZE, CELL_SIZE))

food_img = pygame.image.load(os.path.join(ASSET_PATH, "food.png")).convert_alpha()
food_img = pygame.transform.scale(food_img, (CELL_SIZE, CELL_SIZE))





# ---- Agent Sprites ----
agent_a_img = pygame.image.load(os.path.join(ASSET_PATH, "agent_a.png"))
agent_a_img = pygame.transform.scale(agent_a_img, (AGENT_SCALE, AGENT_SCALE))

agent_b_img = pygame.image.load(os.path.join(ASSET_PATH, "agent_b.png"))
agent_b_img = pygame.transform.scale(agent_b_img, (AGENT_SCALE, AGENT_SCALE))

agent_c_img = pygame.image.load(os.path.join(ASSET_PATH, "agent_c.png"))
agent_c_img = pygame.transform.scale(agent_c_img, (AGENT_SCALE, AGENT_SCALE))


agent_d_img = pygame.image.load(os.path.join(ASSET_PATH, "agent_d.png"))
agent_d_img = pygame.transform.scale(agent_d_img, (AGENT_SCALE, AGENT_SCALE))



character_frames = {
    "down": [],
    "up": [],
    "left": [],
    "right": []
}

for direction in character_frames:
    for i in range(4):
        img = pygame.image.load(
            os.path.join(ASSET_PATH, "character", direction, f"{i}.png")
        ).convert_alpha()

        img = pygame.transform.scale(img, (AGENT_SCALE, AGENT_SCALE))
        character_frames[direction].append(img)

axe_frames = {
    "down": [],
    "up": [],
    "left": [],
    "right": []
}

for direction in ["down","up","left","right"]:
    for i in range(2):

        img = pygame.image.load(
            os.path.join(ASSET_PATH,"axe",f"{direction}_axe",f"{i}.png")
        ).convert_alpha()

        img = pygame.transform.scale(img,(AGENT_SCALE,AGENT_SCALE))
        axe_frames[direction].append(img)


hoe_frames = {
    "down": [],
    "up": [],
    "left": [],
    "right": []
}

for direction in ["down","up","left","right"]:
    for i in range(2):

        img = pygame.image.load(
            os.path.join(ASSET_PATH,"hoe\hoe",f"{direction}_hoe",f"{i}.png")
        ).convert_alpha()

        img = pygame.transform.scale(img,(AGENT_SCALE,AGENT_SCALE))
        hoe_frames[direction].append(img)

# ===============================
# COLORS
# ===============================
RED = (220, 60, 60)
GREEN = (60, 200, 80)
BLUE = (70, 120, 240)
YELLOW = (240, 220, 70)
PURPLE = (180, 80, 220)
ORANGE = (255, 140, 0)
BLACK = (30, 30, 30)

AGENT_COLORS = {
    "A": RED,
    "B": BLUE,
    "C": GREEN
}

# ===============================
# DRAW WORLD
# ===============================
def draw_world(agents, foods, farms, crops, woods,episode, step, energy_packs, dangers , visible_seeds , zoom,action):

    


     # ---- Grass Background ----
    world_surface.blit(ground_img, (0, 0))   



   
    
    # ---- Agent Plots ----
   

    # ---- Food ----
    for fx, fy in foods:
     world_surface.blit(
        food_img,
        (
            fx * CELL_SIZE,
            fy * CELL_SIZE
        )
      )
     
    # ---- Agent Plots ----
    # for agent in agents:
    #     cx, cy = agent.plot_center
    #     half = agent.plot_size // 2
        
    #     for x in range(cx - half, cx + half + 1):
    #         for y in range(cy - half, cy + half + 1):
    #             if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
    #                 screen.blit(
    #                     farmland_img,
    #                     (x * CELL_SIZE, y * CELL_SIZE)
    #                 )          
     

    # ---- Farms (growing) ----
    for (fx, fy), farm in farms.items():
        world_surface.blit(seed_img, (fx * CELL_SIZE, fy * CELL_SIZE))
        
        
    for fx, fy in woods:
     world_surface.blit(wood_img, (fx * CELL_SIZE, fy * CELL_SIZE)) 

    # ---- Crops (ready) ----
    for (fx, fy), owner in crops.items():
        world_surface.blit(crop_img, (fx * CELL_SIZE, fy * CELL_SIZE))

    # # ---- Energy Packs ----
    # for ex, ey in energy_packs:
    #     pygame.draw.rect(
    #         screen,
    #         PURPLE,
    #         (
    #             ex * CELL_SIZE + CELL_SIZE//4,
    #             ey * CELL_SIZE + CELL_SIZE//4,
    #             CELL_SIZE//2,
    #             CELL_SIZE//2
    #         )
    #     )

    # # ---- Danger ----
    # for dx, dy in dangers:
    #     pygame.draw.rect(
    #         screen,
    #         ORANGE,
    #         (
    #             dx * CELL_SIZE,
    #             dy * CELL_SIZE,
    #             CELL_SIZE,
    #             CELL_SIZE
    #         ),
    #         2
    #     )

    # ---- Agents ----
     # ---- Agents ----
    for agent in agents:

     if agent.energy <= 0:
        continue

    # Axe animation
     if agent.is_chopping:

        frame = int(agent.axe_frame)
        img = axe_frames[agent.direction][frame]

        agent.axe_frame += 0.2

        if agent.axe_frame >= 2:
            agent.is_chopping = False

    # Hoe animation
     elif agent.is_farming:

        frame = int(agent.hoe_frame)
        img = hoe_frames[agent.direction][frame]

        agent.hoe_frame += 0.2

        if agent.hoe_frame >= 2:
            agent.is_farming = False

    # Walking animation
     else:

        frame = int(agent.frame)
        img = character_frames[agent.direction][frame]

   
     world_surface.blit(
        img,
        (
            agent.x * CELL_SIZE - (AGENT_SCALE - CELL_SIZE)//2,
            agent.y * CELL_SIZE - (AGENT_SCALE - CELL_SIZE)//2
        )
    )

    # ---- UI Text ----
    ep_text = font.render(f"Episode: {episode}", True, (0, 0, 0))
    step_text = font.render(f"Step: {step}", True, (0, 0, 0))

    world_surface.blit(ep_text, (10, 10))
    world_surface.blit(step_text, (10, 30))
 
   
    scaled_width = int(SCREEN_WIDTH * zoom)
    scaled_height = int(SCREEN_HEIGHT * zoom)

    zoomed_surface = pygame.transform.scale(world_surface, (scaled_width, scaled_height))

    offset_x = (SCREEN_WIDTH - scaled_width) // 2
    offset_y = (SCREEN_HEIGHT - scaled_height) // 2

    screen.fill((0,0,0))
    screen.blit(zoomed_surface, (offset_x, offset_y))
    
    
    pygame.display.flip()
    clock.tick(100)